"""Dublês de HTTP e construtores de dados usados pelos testes."""

import json
from collections.abc import Callable, Sequence

import pandas as pd
import requests

from anp.config import UFS

CABECALHO = (
    "Regiao - Sigla;Estado - Sigla;Municipio;Revenda;CNPJ da Revenda;Nome da Rua;"
    "Numero Rua;Complemento;Bairro;Cep;Produto;Data da Coleta;Valor de Venda;"
    "Valor de Compra;Unidade de Medida;Bandeira"
)

PRECOS_PADRAO = {
    "GASOLINA": "5,00",
    "ETANOL": "3,50",
    "DIESEL S10": "6,00",
    "GASOLINA ADITIVADA": "5,50",
    "DIESEL": "5,80",
    "GNV": "4,00",
}


class FakeResponse:
    def __init__(self, corpo: bytes = b"", status: int = 200, headers: dict | None = None,
                 falha_apos: int | None = None):
        self.corpo = corpo
        self.status_code = status
        self.headers = dict(headers) if headers is not None else {}
        if headers is None and status == 200:
            self.headers["Content-Length"] = str(len(corpo))
        self.falha_apos = falha_apos

    @property
    def text(self) -> str:
        return self.corpo.decode("utf-8")

    def json(self):
        return json.loads(self.corpo)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size: int = 1):
        if self.falha_apos is None:
            yield self.corpo
            return
        yield self.corpo[: self.falha_apos]
        raise requests.ConnectionError("servidor encerrou a conexão")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeSession:
    """Responde por URL (sem query string). O valor é uma FakeResponse ou uma função (url, headers) -> FakeResponse."""

    def __init__(self, rotas: dict[str, FakeResponse | Callable[[str, dict], FakeResponse]]):
        self.rotas = rotas
        self.chamadas: list[tuple[str, dict]] = []

    def get(self, url, headers=None, params=None, stream=False, timeout=None):
        headers = dict(headers or {})
        self.chamadas.append((url, headers))
        chave = url.split("?", 1)[0]
        if chave not in self.rotas:
            raise requests.ConnectionError(f"rota não simulada: {url}")
        alvo = self.rotas[chave]
        return alvo(url, headers) if callable(alvo) else alvo


def linha(uf: str, produto: str, data: str, preco: str, cnpj: str = "00.000.000/0001-00",
          revenda: str = "POSTO TESTE LTDA") -> str:
    return (f"X;{uf};CIDADE;{revenda}; {cnpj};RUA A;1;;CENTRO;00000-000;"
            f"{produto};{data};{preco};;R$ / litro;BRANCA")


def csv_anp(linhas: Sequence[str], encoding: str = "utf-8-sig") -> bytes:
    return ("\r\n".join([CABECALHO, *linhas]) + "\r\n").encode(encoding)


def coletas(data: str, produtos: Sequence[str] = ("GASOLINA", "ETANOL", "DIESEL S10"),
            ufs: Sequence[str] = UFS, precos: dict[str, str] | None = None) -> list[str]:
    """Uma coleta por UF e produto na data dd/mm/aaaa, cada UF com um CNPJ diferente."""
    precos = {**PRECOS_PADRAO, **(precos or {})}
    return [
        linha(uf, produto, data, precos[produto], cnpj=f"{i:02d}.000.000/0001-00")
        for i, uf in enumerate(ufs)
        for produto in produtos
    ]


def diario_sintetico(datas: Sequence[str],
                     preco: Callable[[pd.Timestamp, str, str], float] | None = None,
                     n: int = 10, ufs: Sequence[str] = UFS) -> pd.DataFrame:
    """Base diária (data, uf, produto, soma, n) com n coletas por linha. `preco(data, uf, produto)`."""
    padrao = {"gasolina": 5.0, "etanol": 3.5, "diesel_s10": 6.0}
    preco = preco or (lambda d, uf, p: padrao[p])
    linhas = []
    for d in pd.to_datetime(list(datas)):
        for uf in ufs:
            for p in ("gasolina", "etanol", "diesel_s10"):
                linhas.append({"data": d, "uf": uf, "produto": p, "soma": preco(d, uf, p) * n, "n": n})
    return pd.DataFrame(linhas)
