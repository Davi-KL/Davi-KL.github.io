import json

import pandas as pd
import pytest
from helpers import FakeResponse, FakeSession

from anp.ipca import aplicar_real, fatores, get_ipca, parse_ipca

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
PAYLOAD = [{"data": "01/01/2026", "valor": "10.0"}, {"data": "01/02/2026", "valor": "10.0"}]


def test_parse_ipca():
    df = parse_ipca([{"data": "01/08/2026", "valor": "-0.32"}, {"data": "01/07/2026", "valor": "0.07"}])
    assert df.to_dict("list") == {"mes": ["2026-07", "2026-08"], "variacao": [0.07, -0.32]}


def test_parse_ipca_rejeita_resposta_sem_chaves():
    with pytest.raises(ValueError):
        parse_ipca([{"erro": "x"}])


def test_fatores_levam_valores_para_o_ultimo_mes():
    fator, ref = fatores(parse_ipca(PAYLOAD))
    assert ref == "2026-02"
    assert fator["2026-01"] == pytest.approx(1.1)
    assert fator["2026-02"] == pytest.approx(1.0)


def test_aplicar_real():
    fator, ref = fatores(parse_ipca(PAYLOAD))
    mensal = pd.DataFrame({"mes": ["2025-12", "2026-01", "2026-02", "2026-03"], "preco_medio": [5.0, 5.0, 5.0, 5.0]})
    out = aplicar_real(mensal, fator, ref)
    assert pd.isna(out["real"].iloc[0])  # antes do início da série do IPCA
    assert out["real"].iloc[1:].tolist() == pytest.approx([5.5, 5.0, 5.0])


def test_get_ipca_sucesso_grava_cache(tmp_path):
    cache = tmp_path / "ipca.csv"
    s = FakeSession({URL: FakeResponse(json.dumps(PAYLOAD).encode())})
    df, em_cache = get_ipca(s, cache)
    assert em_cache is False
    assert df["mes"].tolist() == ["2026-01", "2026-02"]
    assert cache.read_text(encoding="utf-8") == "mes,variacao\n2026-01,10.00\n2026-02,10.00\n"


def test_get_ipca_usa_cache_quando_api_falha(tmp_path):
    cache = tmp_path / "ipca.csv"
    cache.write_text("mes,variacao\n2026-01,0.50\n", encoding="utf-8")
    s = FakeSession({URL: FakeResponse(b"", status=503)})
    df, em_cache = get_ipca(s, cache)
    assert em_cache is True
    assert df.to_dict("list") == {"mes": ["2026-01"], "variacao": [0.5]}


def test_get_ipca_sem_api_e_sem_cache_falha(tmp_path):
    s = FakeSession({URL: FakeResponse(b"", status=503)})
    with pytest.raises(RuntimeError, match="sem cache"):
        get_ipca(s, tmp_path / "ipca.csv")


def test_get_ipca_com_lacuna_usa_cache_quando_existe(tmp_path):
    # Falta 02/2026 no meio da série: sem essa checagem, geraria NaN num ponto arbitrário
    # do meio (não só no início) — a API do BCB não deveria conseguir "furar" o IPCA assim.
    com_lacuna = [{"data": "01/01/2026", "valor": "0.5"}, {"data": "01/03/2026", "valor": "0.5"}]
    cache = tmp_path / "ipca.csv"
    cache.write_text("mes,variacao\n2026-01,0.40\n", encoding="utf-8")
    s = FakeSession({URL: FakeResponse(json.dumps(com_lacuna).encode())})
    df, em_cache = get_ipca(s, cache)
    assert em_cache is True
    assert df.to_dict("list") == {"mes": ["2026-01"], "variacao": [0.4]}


def test_get_ipca_com_lacuna_e_sem_cache_falha(tmp_path):
    com_lacuna = [{"data": "01/01/2026", "valor": "0.5"}, {"data": "01/03/2026", "valor": "0.5"}]
    s = FakeSession({URL: FakeResponse(json.dumps(com_lacuna).encode())})
    with pytest.raises(RuntimeError, match="sem cache"):
        get_ipca(s, tmp_path / "ipca.csv")
