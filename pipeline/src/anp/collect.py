"""Downloads com retomada: o servidor da ANP costuma encerrar conexões no meio de arquivos grandes."""

import re
import time
from collections.abc import Callable
from pathlib import Path

import requests

from anp.config import USER_AGENT


class DownloadError(RuntimeError):
    pass


def nome_local(url: str) -> str:
    caminho = url.split("/shpc/", 1)[1] if "/shpc/" in url else url.rsplit("/", 1)[-1]
    return caminho.replace("/", "_")


def _tamanho_total(resposta, inicio: int) -> int | None:
    faixa = resposta.headers.get("Content-Range")
    if faixa:
        achado = re.search(r"/(\d+)$", faixa)
        if achado:
            return int(achado.group(1))
    tamanho = resposta.headers.get("Content-Length")
    if tamanho is None:
        return None
    return int(tamanho) + (inicio if resposta.status_code == 206 else 0)


def fetch_text(url: str, session, *, timeout: int = 60, tentativas: int = 3,
               sleep: Callable[[float], None] = time.sleep) -> str:
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
            resposta.raise_for_status()
            return resposta.text
        except requests.RequestException as erro:
            ultimo_erro = erro
            if tentativa < tentativas:
                sleep(2**tentativa)
    raise DownloadError(f"Falha ao acessar {url} após {tentativas} tentativas: {ultimo_erro}")


def download(url: str, destino_dir: Path, session, *, forcar: bool = False, tentativas: int = 5,
             timeout: int = 60, sleep: Callable[[float], None] = time.sleep) -> Path:
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / nome_local(url)
    if destino.exists() and not forcar:
        return destino
    parcial = destino.with_name(destino.name + ".part")
    if parcial.exists():
        parcial.unlink()

    total: int | None = None
    tamanho = 0
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        inicio = parcial.stat().st_size if parcial.exists() else 0
        headers = {"User-Agent": USER_AGENT}
        if inicio:
            headers["Range"] = f"bytes={inicio}-"
        ultimo_erro = None
        try:
            with session.get(url, headers=headers, stream=True, timeout=timeout) as resposta:
                if resposta.status_code == 416:
                    total = inicio
                else:
                    resposta.raise_for_status()
                    if resposta.status_code == 200:
                        inicio = 0
                    total = _tamanho_total(resposta, inicio)
                    with open(parcial, "ab" if inicio else "wb") as arquivo:
                        for bloco in resposta.iter_content(chunk_size=1 << 20):
                            arquivo.write(bloco)
        except requests.RequestException as erro:
            ultimo_erro = erro

        tamanho = parcial.stat().st_size if parcial.exists() else 0
        completo = tamanho == total if total is not None else ultimo_erro is None
        if completo and tamanho > 0:
            parcial.replace(destino)
            return destino
        if tentativa < tentativas:
            sleep(2**tentativa)

    if parcial.exists():
        parcial.unlink()
    raise DownloadError(
        f"Download incompleto de {url}: {tamanho} bytes (esperado {total}). Último erro: {ultimo_erro}"
    )
