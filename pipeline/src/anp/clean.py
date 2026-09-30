"""Leitura e limpeza dos CSVs da ANP (mesmo cabeçalho de 2004 a 2026)."""

import io
import zipfile
from pathlib import Path

import pandas as pd

from anp.config import PRECO_MAX, PRECO_MIN, PRODUTOS, UFS

COLUNAS = {
    "CNPJ da Revenda": "cnpj",
    "Estado - Sigla": "uf",
    "Produto": "produto",
    "Data da Coleta": "data",
    "Valor de Venda": "preco",
}


class SchemaError(ValueError):
    pass


def _bytes_csv(path: Path) -> bytes:
    conteudo = path.read_bytes()
    if conteudo[:4] != b"PK\x03\x04":
        return conteudo
    with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
        csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(csvs) != 1:
            raise SchemaError(f"{path.name}: esperado 1 CSV dentro do ZIP, encontrados {csvs}")
        return z.read(csvs[0])


def _decodificar(conteudo: bytes) -> str:
    try:
        return conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        return conteudo.decode("latin-1")


def load_raw(path: Path) -> pd.DataFrame:
    texto = _decodificar(_bytes_csv(path))
    cabecalho = [c.strip() for c in pd.read_csv(io.StringIO(texto), sep=";", nrows=0).columns]
    faltando = [c for c in COLUNAS if c not in cabecalho]
    if faltando:
        raise SchemaError(f"{path.name}: colunas ausentes {faltando}. Encontradas: {cabecalho}")
    df = pd.read_csv(
        io.StringIO(texto),
        sep=";",
        dtype=str,
        usecols=lambda c: c.strip() in COLUNAS,
        on_bad_lines="warn",
    )
    df = df.rename(columns=lambda c: COLUNAS[c.strip()])
    return df[list(COLUNAS.values())]


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.assign(
        cnpj=raw["cnpj"].str.strip(),
        uf=raw["uf"].str.strip().str.upper(),
        produto=raw["produto"].str.strip().str.upper().map(PRODUTOS),
        data=pd.to_datetime(raw["data"].str.strip(), format="%d/%m/%Y", errors="coerce"),
        preco=pd.to_numeric(raw["preco"].str.strip().str.replace(",", ".", regex=False), errors="coerce"),
    )
    df = df.dropna(subset=["produto", "data", "preco"])
    df = df[df["uf"].isin(UFS) & df["preco"].between(PRECO_MIN, PRECO_MAX)]
    df = df.drop_duplicates(subset=["cnpj", "produto", "data"])
    return df[["data", "uf", "produto", "preco"]].reset_index(drop=True)
