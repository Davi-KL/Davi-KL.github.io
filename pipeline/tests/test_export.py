import json
import shutil
from datetime import datetime, timezone

import jsonschema
import pandas as pd
import pytest
from helpers import diario_sintetico

from anp.aggregate import monthly
from anp.config import SCHEMAS_DIR, UFS
from anp.export import (
    ARQUIVOS,
    build_etanol_gasolina,
    build_evolucao,
    build_meta,
    build_ranking,
    export_all,
)
from anp.ipca import aplicar_real, fatores, parse_ipca

AGORA = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)
# segundas-feiras de 30/06/2025 a 20/07/2026 (56 semanas)
DATAS = pd.date_range("2025-06-30", "2026-07-20", freq="7D").strftime("%Y-%m-%d").tolist()


def _preco(d, uf, p):
    if p == "gasolina":
        if uf == "DF":
            return 7.2 if d >= pd.Timestamp("2026-06-29") else 6.0  # +20% na janela atual
        return 5.0
    if p == "etanol":
        return 3.0 if uf == "SP" else 3.5
    return 6.0


def _ipca():
    meses = pd.period_range("2025-06", "2026-06", freq="M")
    return parse_ipca([{"data": f"01/{m.month:02d}/{m.year}", "valor": "0.5"} for m in meses])


@pytest.fixture
def diario():
    return diario_sintetico(DATAS, preco=_preco)


@pytest.fixture
def mensal(diario):
    fator, ref = fatores(_ipca())
    return aplicar_real(monthly(diario), fator, ref)


def test_evolucao_meses_continuos_e_series_alinhadas(mensal):
    evo = build_evolucao(mensal, "2026-06")
    assert evo["meses"][0] == "2025-06" and evo["meses"][-1] == "2026-07"
    assert len(evo["meses"]) == 14
    assert set(evo["series"]) == {"BR", *UFS}
    for produtos in evo["series"].values():
        for serie in produtos.values():
            assert len(serie["nominal"]) == len(serie["real"]) == 14
    br_gas = evo["series"]["BR"]["gasolina"]
    idx_ref = evo["meses"].index("2026-06")
    assert br_gas["real"][idx_ref] == br_gas["nominal"][idx_ref]
    assert br_gas["real"][-1] == br_gas["nominal"][-1]  # mês depois do último IPCA
    assert br_gas["real"][0] > br_gas["nominal"][0]  # valor antigo corrigido para cima


def test_ranking_janela_e_variacao_12_meses(diario):
    r = build_ranking(diario)
    assert r["periodo"] == {"inicio": "2026-06-29", "fim": "2026-07-20"}
    itens = {(i["uf"], i["produto"]): i for i in r["itens"]}
    assert itens[("DF", "gasolina")]["preco_medio"] == pytest.approx(7.2)
    assert itens[("DF", "gasolina")]["variacao_12m_pct"] == pytest.approx(20.0)
    assert itens[("SP", "gasolina")]["variacao_12m_pct"] == pytest.approx(0.0)
    assert ("BR", "gasolina") in itens
    assert itens[("DF", "gasolina")]["n_coletas"] == 40  # 4 semanas × 10 coletas


def test_etanol_gasolina_compensa_abaixo_de_70(diario, mensal):
    ranking = build_ranking(diario)
    eg = build_etanol_gasolina(ranking, mensal)
    atual = {a["uf"]: a for a in eg["atual"]}
    assert atual["SP"] == {"uf": "SP", "razao": 0.6, "compensa": "etanol"}
    assert atual["RJ"]["razao"] == 0.7 and atual["RJ"]["compensa"] == "gasolina"  # 0,70 não é "abaixo"
    assert eg["limiar"] == 0.7
    assert len(eg["historico"]["razao"]["SP"]) == len(eg["historico"]["meses"])


def test_meta_destaques(diario, mensal):
    ranking = build_ranking(diario)
    eg = build_etanol_gasolina(ranking, mensal)
    evo = build_evolucao(mensal, "2026-06")
    meta = build_meta(diario, ranking, eg, evo, "2026-06", False, AGORA)
    assert meta["atualizado_em"] == "2026-07-25T12:00:00Z"
    assert meta["semana_mais_recente"] == "2026-07-20"
    assert meta["destaques"]["gasolina_df"] == pytest.approx(7.2)
    assert meta["destaques"]["ufs_etanol_compensa"] == 2  # SP (3,0/5,0) e DF (3,5/7,2)
    assert meta["destaques"]["maior_alta_12m"] == {"uf": "DF", "produto": "gasolina", "pct": 20.0}
    assert len(meta["serie_home"]["meses"]) == 14  # menos de 24 meses disponíveis
    assert len(meta["serie_home"]["gasolina_df"]) == 14


def test_export_all_grava_quatro_arquivos_validos(diario, tmp_path):
    saidas = export_all(diario, _ipca(), False, tmp_path, SCHEMAS_DIR, AGORA)
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(f"{n}.json" for n in ARQUIVOS)
    for nome in ARQUIVOS:
        esquema = json.loads((SCHEMAS_DIR / f"{nome}.schema.json").read_text(encoding="utf-8"))
        conteudo = json.loads((tmp_path / f"{nome}.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(esquema).validate(conteudo)
        assert conteudo == saidas[nome]


def test_export_all_nao_grava_nada_se_um_schema_falhar(diario, tmp_path):
    schemas = tmp_path / "schemas"
    shutil.copytree(SCHEMAS_DIR, schemas)
    meta_schema = json.loads((schemas / "meta.schema.json").read_text(encoding="utf-8"))
    meta_schema["required"].append("campo_que_nao_existe")
    (schemas / "meta.schema.json").write_text(json.dumps(meta_schema), encoding="utf-8")
    saida = tmp_path / "out"
    with pytest.raises(jsonschema.ValidationError):
        export_all(diario, _ipca(), False, saida, schemas, AGORA)
    assert not saida.exists() or not any(saida.iterdir())
