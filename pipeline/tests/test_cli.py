import json
from datetime import datetime, timezone

import pytest
from helpers import FakeResponse, FakeSession, coletas, csv_anp

from anp.cli import executar, main
from anp.config import SCHEMAS_DIR
from anp.validate import ValidationError

PAGINA = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis"
B = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc"
SEMESTRAL = f"{B}/dsas/ca/ca-2026-01.csv"
MENSAL_JUN = f"{B}/dsan/2026/06-dados-abertos-precos-2026-06-gasolina-etanol.csv"
MENSAL_JUL_GE = f"{B}/dsan/2026/07-dados-abertos-precos-gasolina-etanol.csv"
MENSAL_JUL_DG = f"{B}/dsan/2026/07-dados-abertos-precos-diesel-gnv.csv"
QUS_GE = f"{B}/qus/ultimas-4-semanas-gasolina-etanol.csv"
QUS_DG = f"{B}/qus/ultimas-4-semanas-diesel-gnv.csv"
IPCA = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
AGORA = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)

GE = ("GASOLINA", "ETANOL", "GASOLINA ADITIVADA")
DG = ("DIESEL S10", "DIESEL", "GNV")


def _html(*urls):
    return "".join(f'<a href="{u}">x</a>' for u in urls).encode()


def _rotas(qus_ge_linhas=None):
    semestral = coletas("22/06/2026", GE + DG) + coletas("29/06/2026", GE + DG)
    qus_ge = qus_ge_linhas if qus_ge_linhas is not None else coletas("13/07/2026", GE) + coletas("20/07/2026", GE)
    ipca = [{"data": f"01/{m:02d}/2026", "valor": "0.5"} for m in range(1, 7)]
    return {
        PAGINA: FakeResponse(_html(SEMESTRAL, MENSAL_JUN, MENSAL_JUL_GE, MENSAL_JUL_DG, QUS_GE, QUS_DG)),
        SEMESTRAL: FakeResponse(csv_anp(semestral)),
        MENSAL_JUL_GE: FakeResponse(csv_anp(coletas("06/07/2026", GE))),
        MENSAL_JUL_DG: FakeResponse(csv_anp(coletas("06/07/2026", DG))),
        QUS_GE: FakeResponse(csv_anp(qus_ge)),
        QUS_DG: FakeResponse(csv_anp(coletas("13/07/2026", DG) + coletas("20/07/2026", DG))),
        IPCA: FakeResponse(json.dumps(ipca).encode()),
    }


def _dirs(tmp_path):
    return {
        "raw_dir": tmp_path / "raw",
        "processed_dir": tmp_path / "processed",
        "out_dir": tmp_path / "out",
        "schemas_dir": SCHEMAS_DIR,
    }


def test_backfill_gera_base_e_quatro_jsons(tmp_path):
    s = FakeSession(_rotas())
    executar("backfill", session=s, agora=AGORA, **_dirs(tmp_path))
    out = tmp_path / "out"
    assert sorted(p.name for p in out.iterdir()) == [
        "etanol_gasolina.json", "evolucao.json", "meta.json", "ranking_uf.json",
    ]
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    assert meta["semana_mais_recente"] == "2026-07-20"
    assert meta["destaques"]["gasolina_df"] == 5.0
    assert (tmp_path / "processed" / "diario_2026.csv").exists()
    assert (tmp_path / "processed" / "ipca.csv").exists()
    urls = [u for u, _ in s.chamadas]
    assert MENSAL_JUN not in urls  # junho já veio no semestral


def test_update_com_os_mesmos_dados_nao_altera_a_base(tmp_path):
    executar("backfill", session=FakeSession(_rotas()), agora=AGORA, **_dirs(tmp_path))
    processed = tmp_path / "processed"
    antes = {p.name: p.read_bytes() for p in processed.iterdir()}
    executar("update", session=FakeSession(_rotas()), agora=AGORA, **_dirs(tmp_path))
    depois = {p.name: p.read_bytes() for p in processed.iterdir()}
    assert antes == depois


def test_update_sem_base_pede_backfill(tmp_path):
    with pytest.raises(RuntimeError, match="backfill"):
        executar("update", session=FakeSession(_rotas()), agora=AGORA, **_dirs(tmp_path))


def test_falha_de_validacao_nao_grava_nada(tmp_path):
    sem_df = [l for l in coletas("20/07/2026", GE) if ";DF;" not in l]
    rotas = _rotas(qus_ge_linhas=coletas("13/07/2026", GE) + sem_df)
    with pytest.raises(ValidationError):
        executar("backfill", session=FakeSession(rotas), agora=AGORA, **_dirs(tmp_path))
    assert not (tmp_path / "out").exists()
    assert not list((tmp_path / "processed").glob("diario_*.csv"))


def test_main_devolve_1_e_mensagem_clara_em_erro(tmp_path, capsys, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("ANP fora do ar")
    monkeypatch.setattr("anp.cli.executar", explode)
    codigo = main(["update", "--raw-dir", str(tmp_path)])
    assert codigo == 1
    assert "ERRO: ANP fora do ar" in capsys.readouterr().err
