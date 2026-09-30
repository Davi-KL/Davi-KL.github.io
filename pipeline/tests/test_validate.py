from datetime import date

import pandas as pd
import pytest
from helpers import diario_sintetico

from anp.config import UFS
from anp.validate import ValidationError, validate

HOJE = date(2026, 7, 25)
DATAS = ["2026-07-13", "2026-07-20"]


def test_base_valida_passa():
    validate(diario_sintetico(DATAS), pd.Timestamp("2026-07-13"), HOJE)


def test_base_vazia_falha():
    with pytest.raises(ValidationError):
        validate(diario_sintetico([]), None, HOJE)


def test_data_futura_falha():
    with pytest.raises(ValidationError, match="data futura"):
        validate(diario_sintetico(["2026-07-20", "2026-07-27"]), None, HOJE)


def test_base_nao_pode_andar_para_tras():
    with pytest.raises(ValidationError, match="anterior"):
        validate(diario_sintetico(DATAS), pd.Timestamp("2026-07-27"), date(2026, 8, 1))


def test_ultima_semana_precisa_das_27_ufs_na_gasolina():
    base = diario_sintetico(DATAS)
    sem_df = base[~((base.uf == "DF") & (base.data == pd.Timestamp("2026-07-20")) & (base.produto == "gasolina"))]
    with pytest.raises(ValidationError, match="DF"):
        validate(sem_df, None, HOJE)


def test_ultima_semana_precisa_das_27_ufs_tambem_para_diesel_e_etanol():
    # A checagem não pode olhar só gasolina: se o link de diesel sumir da página da ANP,
    # o produto pararia de ser atualizado sem que nenhuma validação percebesse.
    base = diario_sintetico(DATAS)
    sem_diesel_df = base[~((base.uf == "DF") & (base.data == pd.Timestamp("2026-07-20")) & (base.produto == "diesel_s10"))]
    with pytest.raises(ValidationError, match="diesel_s10.*DF|DF.*diesel_s10"):
        validate(sem_diesel_df, None, HOJE)


def test_variacao_semanal_de_25_por_cento_falha():
    def preco(d, uf, p):
        if p == "gasolina":
            return 5.0 if d == pd.Timestamp("2026-07-13") else 6.25  # +25%
        return 4.0
    with pytest.raises(ValidationError, match="variou"):
        validate(diario_sintetico(DATAS, preco=preco), None, HOJE)


def test_variacao_de_24_por_cento_passa():
    def preco(d, uf, p):
        if p == "gasolina":
            return 5.0 if d == pd.Timestamp("2026-07-13") else 6.2
        return 4.0
    validate(diario_sintetico(DATAS, preco=preco), None, HOJE)


def test_media_diaria_fora_da_faixa_falha():
    base = diario_sintetico(DATAS)
    base.loc[0, "soma"] = 999.0 * base.loc[0, "n"]
    with pytest.raises(ValidationError, match="fora da faixa"):
        validate(base, None, HOJE)


def test_lista_todos_os_erros_de_uma_vez():
    base = diario_sintetico(["2026-07-20", "2026-07-27"], ufs=[u for u in UFS if u != "AC"])
    with pytest.raises(ValidationError) as erro:
        validate(base, None, HOJE)
    # data futura + AC ausente nos 3 produtos (gasolina, etanol, diesel_s10)
    assert len(erro.value.erros) == 4
