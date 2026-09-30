"""IPCA mensal (Banco Central, série SGS 433) e fatores para reais constantes."""

from pathlib import Path

import pandas as pd
import requests

from anp.config import BCB_IPCA_URL, USER_AGENT


def parse_ipca(payload: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(payload)
    if df.empty or not {"data", "valor"} <= set(df.columns):
        raise ValueError("Resposta do BCB sem as chaves 'data' e 'valor'")
    out = pd.DataFrame({
        "mes": pd.to_datetime(df["data"], format="%d/%m/%Y").dt.strftime("%Y-%m"),
        "variacao": pd.to_numeric(df["valor"]),
    })
    return out.sort_values("mes").reset_index(drop=True)


def _tem_lacuna(ipca: pd.DataFrame) -> bool:
    """True se faltar algum mês entre o primeiro e o último da série (BCB já entregou séries cortadas)."""
    esperado = set(pd.period_range(ipca["mes"].min(), ipca["mes"].max(), freq="M").strftime("%Y-%m"))
    return esperado != set(ipca["mes"])


def get_ipca(session, cache: Path, timeout: int = 30) -> tuple[pd.DataFrame, bool]:
    try:
        resposta = session.get(
            BCB_IPCA_URL,
            headers={"User-Agent": USER_AGENT},
            params={"dataInicial": "01/01/2004"},
            timeout=timeout,
        )
        resposta.raise_for_status()
        df = parse_ipca(resposta.json())
        if _tem_lacuna(df):
            raise ValueError("Série do IPCA recebida com lacunas (meses faltando no meio)")
    except (requests.RequestException, ValueError) as erro:
        if not cache.exists():
            raise RuntimeError(f"IPCA indisponível e sem cache em {cache}: {erro}") from erro
        return pd.read_csv(cache, dtype={"mes": str}), True
    cache.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, index=False, float_format="%.2f", lineterminator="\n")
    return df, False


def fatores(ipca: pd.DataFrame) -> tuple[pd.Series, str]:
    indice = (1 + ipca["variacao"] / 100).cumprod()
    indice.index = ipca["mes"].tolist()
    ref = ipca["mes"].iloc[-1]
    return indice.loc[ref] / indice, ref


def aplicar_real(mensal: pd.DataFrame, fator: pd.Series, ref: str) -> pd.DataFrame:
    f = mensal["mes"].map(fator)
    f = f.where(mensal["mes"] <= ref, 1.0)
    return mensal.assign(real=mensal["preco_medio"] * f)
