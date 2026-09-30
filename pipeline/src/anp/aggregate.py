"""Agregações a partir da base diária (soma de preços e número de coletas).

Todas as médias são ponderadas pelo número de coletas. A linha "BR" soma as
coletas de todas as UFs, em vez de tirar a média das médias estaduais.
"""

import pandas as pd


def daily(limpo: pd.DataFrame) -> pd.DataFrame:
    agregado = limpo.groupby(["data", "uf", "produto"], as_index=False).agg(
        soma=("preco", "sum"), n=("preco", "size")
    )
    return agregado.sort_values(["data", "uf", "produto"]).reset_index(drop=True)


def _media(df: pd.DataFrame, chave: str) -> pd.DataFrame:
    por_uf = df.groupby([chave, "uf", "produto"], as_index=False)[["soma", "n"]].sum()
    br = por_uf.groupby([chave, "produto"], as_index=False)[["soma", "n"]].sum().assign(uf="BR")
    todos = pd.concat([por_uf, br], ignore_index=True)
    todos["preco_medio"] = todos["soma"] / todos["n"]
    colunas = [chave, "uf", "produto", "preco_medio", "n"]
    return todos[colunas].sort_values([chave, "uf", "produto"]).reset_index(drop=True)


def inicio_semana(datas: pd.Series) -> pd.Series:
    return (datas - pd.to_timedelta(datas.dt.dayofweek, unit="D")).dt.normalize()


def weekly(diario: pd.DataFrame) -> pd.DataFrame:
    return _media(diario.assign(semana=inicio_semana(diario["data"])), "semana")


def monthly(diario: pd.DataFrame) -> pd.DataFrame:
    return _media(diario.assign(mes=diario["data"].dt.strftime("%Y-%m")), "mes")


def window_mean(diario: pd.DataFrame, inicio: pd.Timestamp, fim: pd.Timestamp) -> pd.DataFrame:
    recorte = diario[(diario["data"] >= inicio) & (diario["data"] <= fim)]
    return _media(recorte.assign(janela=0), "janela").drop(columns="janela")


def janela_4_semanas(ultima_data: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    fim = ultima_data.normalize()
    segunda = fim - pd.Timedelta(days=fim.dayofweek)
    return segunda - pd.Timedelta(weeks=3), fim
