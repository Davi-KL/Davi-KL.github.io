"""Base diária versionada: upsert por (data, produto) e armazenamento particionado por ano.

Os arquivos da ANP são cortados por data de calendário e por grupo de produtos
(gasolina/etanol e diesel/GNV). Por isso o upsert usa a chave (data, produto): um
arquivo novo é a verdade para as datas e produtos que ele contém, e não mexe no resto.
"""

from pathlib import Path

import pandas as pd

COLUNAS_BASE = ["data", "uf", "produto", "soma", "n"]


def base_vazia() -> pd.DataFrame:
    return pd.DataFrame({
        "data": pd.Series(dtype="datetime64[ns]"),
        "uf": pd.Series(dtype=str),
        "produto": pd.Series(dtype=str),
        "soma": pd.Series(dtype=float),
        "n": pd.Series(dtype="int64"),
    })


def _chave(df: pd.DataFrame) -> pd.Series:
    return df["data"].dt.strftime("%Y-%m-%d") + "|" + df["produto"]


def upsert(base: pd.DataFrame, novo: pd.DataFrame) -> pd.DataFrame:
    if base.empty:
        mantidos = base_vazia()
    else:
        mantidos = base[~_chave(base).isin(set(_chave(novo)))]
    partes = [p for p in (mantidos, novo[COLUNAS_BASE]) if not p.empty]
    if not partes:
        return base_vazia()
    out = pd.concat(partes, ignore_index=True)
    out["n"] = out["n"].astype("int64")
    return out.sort_values(["data", "uf", "produto"]).reset_index(drop=True)[COLUNAS_BASE]


def load_base(pasta: Path) -> pd.DataFrame:
    arquivos = sorted(pasta.glob("diario_*.csv"))
    if not arquivos:
        return base_vazia()
    df = pd.concat(
        [pd.read_csv(a, dtype={"uf": str, "produto": str, "n": "int64"}) for a in arquivos],
        ignore_index=True,
    )
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d")
    return df.sort_values(["data", "uf", "produto"]).reset_index(drop=True)[COLUNAS_BASE]


def save_base(df: pd.DataFrame, pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    for ano, parte in df.groupby(df["data"].dt.year):
        parte[COLUNAS_BASE].to_csv(
            pasta / f"diario_{ano}.csv",
            index=False,
            date_format="%Y-%m-%d",
            float_format="%.4f",
            lineterminator="\n",
        )
