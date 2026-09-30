"""Constantes e caminhos do pipeline."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PIPELINE_DIR = REPO_ROOT / "pipeline"
RAW_DIR = PIPELINE_DIR / "data" / "raw"
PROCESSED_DIR = PIPELINE_DIR / "data" / "processed"
OUT_DIR = REPO_ROOT / "site" / "public" / "data"
SCHEMAS_DIR = REPO_ROOT / "schemas"

ANP_PAGE_URL = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
    "serie-historica-de-precos-de-combustiveis"
)
BCB_IPCA_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
USER_AGENT = "Mozilla/5.0 (compatible; anp-pipeline; +https://github.com/Davi-KL)"

PRODUTOS = {"GASOLINA": "gasolina", "ETANOL": "etanol", "DIESEL S10": "diesel_s10"}
ORDEM_PRODUTOS = ["gasolina", "etanol", "diesel_s10"]
UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

PRECO_MIN = 0.50
PRECO_MAX = 20.00
LIMIAR_ETANOL = 0.70
MAX_VARIACAO_SEMANAL = 0.25
