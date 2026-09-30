import pandas as pd
import pytest

from anp.aggregate import daily, weekly
from anp.merge import COLUNAS_BASE, base_vazia, load_base, save_base, upsert


def _diario(linhas):
    limpo = pd.DataFrame(linhas, columns=["data", "uf", "produto", "preco"]).assign(
        data=lambda d: pd.to_datetime(d["data"])
    )
    return daily(limpo)


def test_upsert_em_base_vazia():
    novo = _diario([("2026-07-20", "DF", "gasolina", 6.0)])
    out = upsert(base_vazia(), novo)
    assert list(out.columns) == COLUNAS_BASE
    assert len(out) == 1


def test_upsert_substitui_mesma_data_e_produto():
    base = _diario([("2026-07-20", "DF", "gasolina", 6.0), ("2026-07-20", "SP", "gasolina", 5.0)])
    novo = _diario([("2026-07-20", "DF", "gasolina", 6.5)])  # revisão da ANP, só DF
    out = upsert(base, novo)
    assert len(out) == 1  # a data inteira daquele produto vem do arquivo novo
    assert out.iloc[0]["soma"] == pytest.approx(6.5)


def test_upsert_nao_apaga_outro_produto_na_mesma_data():
    diesel = _diario([("2026-07-20", "DF", "diesel_s10", 7.0)])
    gasolina_etanol = _diario([("2026-07-20", "DF", "gasolina", 6.0), ("2026-07-20", "DF", "etanol", 4.0)])
    out = upsert(diesel, gasolina_etanol)
    assert sorted(out["produto"]) == ["diesel_s10", "etanol", "gasolina"]


def test_semana_dividida_entre_dois_arquivos_fica_completa():
    semestral = _diario([("2026-06-29", "DF", "gasolina", 6.0), ("2026-06-30", "DF", "gasolina", 6.0)])
    mensal_julho = _diario([("2026-07-01", "DF", "gasolina", 9.0)])
    base = upsert(upsert(base_vazia(), semestral), mensal_julho)
    s = weekly(base)
    linha = s[(s.uf == "DF") & (s.semana == pd.Timestamp("2026-06-29"))].iloc[0]
    assert linha["preco_medio"] == pytest.approx(7.0)  # (6+6+9)/3
    assert linha["n"] == 3


def test_upsert_idempotente():
    base = _diario([("2026-07-13", "DF", "gasolina", 6.0)])
    novo = _diario([("2026-07-13", "DF", "gasolina", 6.1), ("2026-07-20", "DF", "gasolina", 6.2)])
    uma_vez = upsert(base, novo)
    duas_vezes = upsert(uma_vez, novo)
    pd.testing.assert_frame_equal(uma_vez, duas_vezes)


def test_save_e_load_particionado_por_ano(tmp_path):
    base = _diario([
        ("2025-12-29", "DF", "gasolina", 6.123456),
        ("2026-01-05", "DF", "gasolina", 6.2),
    ])
    save_base(base, tmp_path)
    assert sorted(p.name for p in tmp_path.glob("diario_*.csv")) == ["diario_2025.csv", "diario_2026.csv"]
    assert (tmp_path / "diario_2025.csv").read_text(encoding="utf-8") == (
        "data,uf,produto,soma,n\n2025-12-29,DF,gasolina,6.1235,1\n"
    )
    lida = load_base(tmp_path)
    assert list(lida.columns) == COLUNAS_BASE
    assert lida["data"].tolist() == [pd.Timestamp("2025-12-29"), pd.Timestamp("2026-01-05")]
    assert lida["n"].tolist() == [1, 1]


def test_load_base_de_pasta_vazia(tmp_path):
    assert load_base(tmp_path).empty
