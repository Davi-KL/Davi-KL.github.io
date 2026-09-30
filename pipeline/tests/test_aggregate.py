import pandas as pd
import pytest

from anp.aggregate import daily, inicio_semana, janela_4_semanas, monthly, weekly, window_mean


def _limpo(linhas):
    return pd.DataFrame(linhas, columns=["data", "uf", "produto", "preco"]).assign(
        data=lambda d: pd.to_datetime(d["data"])
    )


def test_daily_soma_precos_e_conta_coletas():
    limpo = _limpo([
        ("2026-01-12", "DF", "gasolina", 6.0),
        ("2026-01-12", "DF", "gasolina", 6.4),
        ("2026-01-12", "SP", "gasolina", 5.0),
    ])
    d = daily(limpo)
    df_linha = d[(d.uf == "DF")].iloc[0]
    assert df_linha["soma"] == pytest.approx(12.4)
    assert df_linha["n"] == 2
    assert len(d) == 2


def test_media_nacional_usa_todas_as_coletas_e_nao_a_media_das_ufs():
    diario = daily(_limpo([
        ("2026-01-12", "AC", "gasolina", 4.0),
        ("2026-01-12", "AC", "gasolina", 4.0),
        ("2026-01-13", "SP", "gasolina", 7.0),
    ]))
    s = weekly(diario)
    br = s[s.uf == "BR"].iloc[0]
    assert br["preco_medio"] == pytest.approx(5.0)  # (4+4+7)/3, e não (4+7)/2 = 5.5
    assert br["n"] == 3


def test_semana_comeca_na_segunda_feira():
    datas = pd.Series(pd.to_datetime(["2026-07-20", "2026-07-22", "2026-07-26"]))  # seg, qua, dom
    assert list(inicio_semana(datas)) == [pd.Timestamp("2026-07-20")] * 3


def test_weekly_junta_dias_da_mesma_semana():
    diario = daily(_limpo([
        ("2026-06-29", "DF", "etanol", 4.0),  # segunda
        ("2026-07-01", "DF", "etanol", 5.0),  # quarta (outro mês, mesma semana)
    ]))
    s = weekly(diario)
    linha = s[(s.uf == "DF")].iloc[0]
    assert linha["semana"] == pd.Timestamp("2026-06-29")
    assert linha["preco_medio"] == pytest.approx(4.5)


def test_monthly_agrupa_por_mes_de_calendario():
    diario = daily(_limpo([
        ("2026-06-29", "DF", "etanol", 4.0),
        ("2026-07-01", "DF", "etanol", 5.0),
    ]))
    m = monthly(diario)
    df_m = m[m.uf == "DF"].set_index("mes")["preco_medio"].to_dict()
    assert df_m == {"2026-06": pytest.approx(4.0), "2026-07": pytest.approx(5.0)}


def test_window_mean_respeita_limites_inclusivos():
    diario = daily(_limpo([
        ("2026-06-28", "DF", "gasolina", 9.0),
        ("2026-06-29", "DF", "gasolina", 6.0),
        ("2026-07-20", "DF", "gasolina", 7.0),
        ("2026-07-21", "DF", "gasolina", 9.0),
    ]))
    w = window_mean(diario, pd.Timestamp("2026-06-29"), pd.Timestamp("2026-07-20"))
    df_w = w[w.uf == "DF"].iloc[0]
    assert df_w["preco_medio"] == pytest.approx(6.5)
    assert set(w.columns) == {"uf", "produto", "preco_medio", "n"}


def test_window_mean_vazia_nao_quebra():
    diario = daily(_limpo([("2026-07-20", "DF", "gasolina", 7.0)]))
    w = window_mean(diario, pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-31"))
    assert w.empty


def test_janela_4_semanas_a_partir_de_uma_quarta():
    inicio, fim = janela_4_semanas(pd.Timestamp("2026-07-22"))
    assert inicio == pd.Timestamp("2026-06-29")
    assert fim == pd.Timestamp("2026-07-22")
