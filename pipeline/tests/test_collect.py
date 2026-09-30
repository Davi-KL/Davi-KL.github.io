import pytest
from helpers import FakeResponse, FakeSession

from anp.collect import DownloadError, download, fetch_text, nome_local

URL = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/ca/ca-2021-02.csv"
CORPO = b"0123456789" * 10
SEM_ESPERA = {"sleep": lambda _s: None}


def _parcial(inicio: int) -> FakeResponse:
    return FakeResponse(
        CORPO[inicio:],
        status=206,
        headers={
            "Content-Range": f"bytes {inicio}-{len(CORPO) - 1}/{len(CORPO)}",
            "Content-Length": str(len(CORPO) - inicio),
        },
    )


def test_nome_local_usa_caminho_depois_de_shpc():
    assert nome_local(URL) == "dsas_ca_ca-2021-02.csv"
    assert nome_local(".../shpc/dsan/2023/precos-diesel-gnv-01.csv") == "dsan_2023_precos-diesel-gnv-01.csv"


def test_download_completo_de_primeira(tmp_path):
    s = FakeSession({URL: FakeResponse(CORPO)})
    caminho = download(URL, tmp_path, s, **SEM_ESPERA)
    assert caminho.read_bytes() == CORPO
    assert not list(tmp_path.glob("*.part"))


def test_retoma_download_interrompido_com_range(tmp_path):
    def rota(url, headers):
        if "Range" not in headers:
            return FakeResponse(CORPO, falha_apos=40)
        inicio = int(headers["Range"].removeprefix("bytes=").rstrip("-"))
        return _parcial(inicio)

    s = FakeSession({URL: rota})
    caminho = download(URL, tmp_path, s, **SEM_ESPERA)
    assert caminho.read_bytes() == CORPO
    assert s.chamadas[1][1]["Range"] == "bytes=40-"


def test_servidor_que_ignora_range_reinicia_o_arquivo(tmp_path):
    respostas = iter([FakeResponse(CORPO, falha_apos=40), FakeResponse(CORPO)])
    s = FakeSession({URL: lambda url, headers: next(respostas)})
    caminho = download(URL, tmp_path, s, **SEM_ESPERA)
    assert caminho.read_bytes() == CORPO


def test_falha_permanente_levanta_erro_sem_criar_arquivo(tmp_path):
    s = FakeSession({URL: FakeResponse(b"", status=503)})
    with pytest.raises(DownloadError):
        download(URL, tmp_path, s, tentativas=3, **SEM_ESPERA)
    assert not (tmp_path / nome_local(URL)).exists()
    assert len(s.chamadas) == 3


def test_arquivo_em_cache_nao_baixa_de_novo(tmp_path):
    (tmp_path / nome_local(URL)).write_bytes(b"antigo")
    s = FakeSession({})
    caminho = download(URL, tmp_path, s, **SEM_ESPERA)
    assert caminho.read_bytes() == b"antigo"
    assert s.chamadas == []


def test_forcar_baixa_de_novo(tmp_path):
    (tmp_path / nome_local(URL)).write_bytes(b"antigo")
    s = FakeSession({URL: FakeResponse(CORPO)})
    caminho = download(URL, tmp_path, s, forcar=True, **SEM_ESPERA)
    assert caminho.read_bytes() == CORPO


def test_fetch_text_tenta_de_novo_e_devolve_texto():
    respostas = iter([FakeResponse(b"", status=500), FakeResponse("<html>ok</html>".encode())])
    s = FakeSession({URL: lambda url, headers: next(respostas)})
    assert fetch_text(URL, s, **SEM_ESPERA) == "<html>ok</html>"


def test_fetch_text_desiste_depois_das_tentativas():
    s = FakeSession({URL: FakeResponse(b"", status=500)})
    with pytest.raises(DownloadError):
        fetch_text(URL, s, tentativas=2, **SEM_ESPERA)
