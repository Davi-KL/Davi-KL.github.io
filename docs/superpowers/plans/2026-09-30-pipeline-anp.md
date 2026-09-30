# Pipeline de Dados ANP — Plano de Implementação (Parte 1 de 2)

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: use superpowers:subagent-driven-development (recomendado) ou superpowers:executing-plans para implementar este plano tarefa por tarefa. Os passos usam checkbox (`- [ ]`) para acompanhamento.

**Objetivo:** construir o pipeline em Python que coleta a Série Histórica de Preços de Combustíveis da ANP, limpa, agrega, corrige pelo IPCA e exporta quatro JSONs validados, com atualização semanal via GitHub Actions.

**Arquitetura:** um pacote Python (`pipeline/src/anp`) com um módulo por etapa: links → collect → clean → aggregate → merge → ipca → validate → export → cli. A fonte da verdade é uma base **diária** versionada (`soma` de preços e `n` de coletas por data × UF × produto). Todas as médias saem dela. O site (Parte 2) só conhece os JSONs em `site/public/data/`, cujo formato é fixado pelos JSON Schemas em `schemas/`.

**Tecnologias:** Python ≥ 3.11 (CI em 3.12), pandas, requests, jsonschema, pytest.

**Spec:** `docs/superpowers/specs/2026-09-30-portfolio-design.md`. A seção 9 ("Ajustes após verificar as fontes") prevalece sobre as seções 4.1 e 4.3.

**Parte 2:** `docs/superpowers/plans/2026-09-30-site-portfolio.md` (site Vue + deploy). Ela depende dos schemas criados na Tarefa 9 deste plano.

## Restrições globais

- Todos os comandos rodam no Git Bash, a partir da raiz do repositório (`Curso _ Renato Asse/`), salvo quando o passo diz `cd pipeline`.
- O Python do projeto é `pipeline/.venv/Scripts/python` (Windows). No CI (Linux) é o `python` do `setup-python`.
- Dependências: `pandas>=2.2,<4`, `requests>=2.32,<3`, `jsonschema>=4.23,<5` e, para desenvolvimento, `pytest>=8`. Não adicione outras.
- **Os testes nunca acessam a rede.** Todo HTTP passa por um objeto `session` injetado, e os testes usam `FakeSession` (`pipeline/tests/helpers.py`).
- Página de links da ANP: `https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis`
- API do IPCA: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json`
- Produtos mantidos, com os nomes exatos da ANP: `GASOLINA` → `gasolina`, `ETANOL` → `etanol`, `DIESEL S10` → `diesel_s10`. Todo o resto é descartado.
- Faixa plausível de preço: R$ 0,50 a R$ 20,00 por litro, inclusive nos dois extremos.
- UFs: as 27 siglas. A região agregada nacional usa a sigla `BR`.
- Limiar etanol/gasolina: `0.70`. Variação semanal máxima da gasolina BR: `0.25`.
- Colunas obrigatórias do CSV da ANP: `CNPJ da Revenda`, `Estado - Sigla`, `Produto`, `Data da Coleta`, `Valor de Venda`. Separador `;`, decimal `,` e data `dd/mm/aaaa`. Codificação `utf-8-sig`, com fallback para `latin-1`.
- Base versionada: `pipeline/data/processed/diario_AAAA.csv` com colunas `data,uf,produto,soma,n` e `pipeline/data/processed/ipca.csv` com colunas `mes,variacao`. Brutos em `pipeline/data/raw/`, fora do git.
- Saídas: `site/public/data/{evolucao,ranking_uf,etanol_gasolina,meta}.json`, validadas contra `schemas/<nome>.schema.json` **antes** de gravar qualquer arquivo.
- Mensagens de commit terminam com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Foco de revisão

1. **Download cortado no meio pelo servidor da ANP.** Aconteceu nos testes reais com 2013-01 e 2021-02. O arquivo precisa ser retomado com `Range` e só é aceito com o tamanho completo. Teste na Tarefa 3.
2. **Arquivo em latin-1 no meio de arquivos UTF-8** (2021-02), com acentos em nomes de revenda. A leitura não pode quebrar. Teste na Tarefa 4.
3. **Nomes de arquivos mensais irregulares:** erro de digitação, sem extensão, padrão de 2023 com o mês no fim. Todos precisam ser classificados com ano, mês e tipo corretos. Teste na Tarefa 2.
4. **Semana dividida entre dois arquivos** (ex.: 29/06 no semestral e 01/07 no mensal), e **arquivo de gasolina/etanol aplicado na mesma data de um arquivo de diesel.** O *upsert* não pode apagar a metade que veio do outro arquivo. Testes na Tarefa 6.
5. **O `meta.json` muda a cada execução** (`atualizado_em`). Rodar o `update` duas vezes com os mesmos dados precisa deixar `pipeline/data/processed/` byte a byte idêntico, senão o workflow faria commit toda semana sem motivo. Teste na Tarefa 10.

---

### Task 1: Pacote Python e configuração

**Arquivos:**
- Criar: `pipeline/pyproject.toml`
- Criar: `pipeline/src/anp/__init__.py`
- Criar: `pipeline/src/anp/config.py`
- Criar: `pipeline/tests/test_config.py`

**Interfaces:**
- Produz: o módulo `anp.config` com `REPO_ROOT`, `PIPELINE_DIR`, `RAW_DIR`, `PROCESSED_DIR`, `OUT_DIR`, `SCHEMAS_DIR` (todos `Path`), `ANP_PAGE_URL`, `BCB_IPCA_URL`, `USER_AGENT` (`str`), `PRODUTOS: dict[str, str]`, `ORDEM_PRODUTOS: list[str]`, `UFS: list[str]`, `PRECO_MIN`, `PRECO_MAX`, `LIMIAR_ETANOL`, `MAX_VARIACAO_SEMANAL` (`float`).

- [ ] **Passo 1: Criar o `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "anp-pipeline"
version = "0.1.0"
description = "Coleta e análise dos preços de combustíveis da ANP para o portfólio de Davi Levy"
requires-python = ">=3.11"
dependencies = [
  "pandas>=2.2,<4",
  "requests>=2.32,<3",
  "jsonschema>=4.23,<5",
]

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
anp = "anp.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Passo 2: Criar o ambiente virtual e instalar**

```bash
cd pipeline
python -m venv .venv
.venv/Scripts/python -m pip install --upgrade pip
.venv/Scripts/python -m pip install -e ".[dev]"
```

Esperado: termina com `Successfully installed ... anp-pipeline-0.1.0 ...`. O `pip` pode falhar dizendo que o pacote `anp` não existe. Nesse caso, crie o `__init__.py` do Passo 3 antes e repita.

- [ ] **Passo 3: Escrever o teste que falha**

`pipeline/src/anp/__init__.py`:

```python
"""Pipeline de dados de preços de combustíveis da ANP."""
```

`pipeline/tests/test_config.py`:

```python
from anp import config


def test_ufs_tem_27_siglas_unicas():
    assert len(config.UFS) == 27
    assert len(set(config.UFS)) == 27
    assert "DF" in config.UFS
    assert "BR" not in config.UFS


def test_produtos_mapeados_com_nomes_da_anp():
    assert config.PRODUTOS == {
        "GASOLINA": "gasolina",
        "ETANOL": "etanol",
        "DIESEL S10": "diesel_s10",
    }
    assert config.ORDEM_PRODUTOS == ["gasolina", "etanol", "diesel_s10"]


def test_caminhos_apontam_para_o_repositorio():
    assert (config.REPO_ROOT / "pipeline" / "pyproject.toml").exists()
    assert config.OUT_DIR == config.REPO_ROOT / "site" / "public" / "data"
    assert config.SCHEMAS_DIR == config.REPO_ROOT / "schemas"
    assert config.PROCESSED_DIR == config.REPO_ROOT / "pipeline" / "data" / "processed"


def test_limites():
    assert (config.PRECO_MIN, config.PRECO_MAX) == (0.50, 20.00)
    assert config.LIMIAR_ETANOL == 0.70
    assert config.MAX_VARIACAO_SEMANAL == 0.25
```

- [ ] **Passo 4: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_config.py -v`
Esperado: FALHA com `ImportError: cannot import name 'config'`.

- [ ] **Passo 5: Implementar `config.py`**

```python
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
```

- [ ] **Passo 6: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_config.py -v`
Esperado: 4 passed.

- [ ] **Passo 7: Commit**

```bash
git add pipeline/pyproject.toml pipeline/src/anp/__init__.py pipeline/src/anp/config.py pipeline/tests/test_config.py
git commit -m "feat(pipeline): pacote anp e configuração" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Descoberta de links na página da ANP

**Arquivos:**
- Criar: `pipeline/src/anp/links.py`
- Criar: `pipeline/tests/test_links.py`

**Interfaces:**
- Produz:
  - `LinkMensal`, um dataclass frozen com os campos `url: str`, `ano: int`, `mes: int` e `tipo: str`. O tipo é `"gasolina-etanol"` ou `"diesel-gnv"`.
  - `LinksAnp`, um dataclass com `semestrais: list[str]`, `mensais: list[LinkMensal]` e `ultimas_semanas: list[str]`.
  - `discover_links(html: str) -> LinksAnp`. As listas vêm ordenadas e sem duplicatas, e os links de GLP são ignorados.

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_links.py` (as URLs são reais, tiradas da página em 30/09/2026):

```python
from anp.links import LinkMensal, discover_links

BASE = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc"

HTML = f"""
<a href="{BASE}/dsas/ca/ca-2004-01.csv">1º sem 2004</a>
<a href="{BASE}/dsas/ca/ca-2026-01.zip">1º sem 2026</a>
<a href="{BASE}/dsas/ca/precos-semestrais-ca.zip">1º sem 2022</a>
<a href="{BASE}/dsas/glp/glp-2026-01.csv">GLP semestral</a>
<a href="{BASE}/dsan/2023/precos-diesel-gnv-01.csv">jan/2023 diesel</a>
<a href="{BASE}/dsan/2023/precos-gasolina-etanol-12.csv">dez/2023 gasolina</a>
<a href="{BASE}/dsan/2026/02-cados-abertos-preco-gasolina-etanol.csv">fev/2026 (erro de digitação)</a>
<a href="{BASE}/dsan/2026/04-dados-abertos-precos-diesel-gnv">abr/2026 (sem extensão)</a>
<a href="{BASE}/dsan/2026/08-dados-abertos-precos-2026-08-gasolina-etanol.csv">ago/2026</a>
<a href="{BASE}/dsan/2026/08-dados-abertos-precos-2026-08-glp.csv">GLP mensal</a>
<a href="{BASE}/qus/ultimas-4-semanas-gasolina-etanol.csv">4 semanas</a>
<a href="{BASE}/qus/ultimas-4-semanas-diesel-gnv.csv">4 semanas</a>
<a href="{BASE}/qus/ultimas-4-semanas-glp.csv">4 semanas GLP</a>
<a href="{BASE}/qus/ultimas-4-semanas-gasolina-etanol.csv">link duplicado</a>
<a href="https://www.gov.br/anp/pt-br/outra-pagina">fora do escopo</a>
"""


def test_semestrais_incluem_zip_de_2022_e_excluem_glp():
    links = discover_links(HTML)
    assert links.semestrais == [
        f"{BASE}/dsas/ca/ca-2004-01.csv",
        f"{BASE}/dsas/ca/ca-2026-01.zip",
        f"{BASE}/dsas/ca/precos-semestrais-ca.zip",
    ]


def test_mensais_classificados_mesmo_com_nomes_irregulares():
    links = discover_links(HTML)
    assert [(m.ano, m.mes, m.tipo) for m in links.mensais] == [
        (2023, 1, "diesel-gnv"),
        (2023, 12, "gasolina-etanol"),
        (2026, 2, "gasolina-etanol"),
        (2026, 4, "diesel-gnv"),
        (2026, 8, "gasolina-etanol"),
    ]
    assert links.mensais[3] == LinkMensal(
        url=f"{BASE}/dsan/2026/04-dados-abertos-precos-diesel-gnv",
        ano=2026,
        mes=4,
        tipo="diesel-gnv",
    )


def test_ultimas_semanas_sem_duplicatas_e_sem_glp():
    links = discover_links(HTML)
    assert links.ultimas_semanas == [
        f"{BASE}/qus/ultimas-4-semanas-diesel-gnv.csv",
        f"{BASE}/qus/ultimas-4-semanas-gasolina-etanol.csv",
    ]


def test_pagina_sem_links_devolve_listas_vazias():
    links = discover_links("<html><body>manutenção</body></html>")
    assert links.semestrais == []
    assert links.mensais == []
    assert links.ultimas_semanas == []
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_links.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.links'`.

- [ ] **Passo 3: Implementar `links.py`**

```python
"""Descobre os links de download na página de dados abertos da ANP.

Os nomes dos arquivos mensais não seguem um padrão fixo: há erros de digitação,
arquivos sem extensão e formatos diferentes por ano. Por isso os links são lidos
da página em vez de montados.
"""

import re
from dataclasses import dataclass, field

_HREF = re.compile(r'href="([^"]+/shpc/[^"]+)"')
_MENSAL = re.compile(r"/dsan/(\d{4})/([^/]+)$")


@dataclass(frozen=True)
class LinkMensal:
    url: str
    ano: int
    mes: int
    tipo: str


@dataclass
class LinksAnp:
    semestrais: list[str] = field(default_factory=list)
    mensais: list[LinkMensal] = field(default_factory=list)
    ultimas_semanas: list[str] = field(default_factory=list)


def _tipo(nome: str) -> str | None:
    nome = nome.lower()
    if "gasolina" in nome:
        return "gasolina-etanol"
    if "diesel" in nome:
        return "diesel-gnv"
    return None


def _mes(nome: str) -> int | None:
    achado = re.match(r"(\d{2})-", nome) or re.search(r"-(\d{2})(?:\.csv)?$", nome)
    if not achado:
        return None
    mes = int(achado.group(1))
    return mes if 1 <= mes <= 12 else None


def discover_links(html: str) -> LinksAnp:
    links = LinksAnp()
    vistos: set[str] = set()
    for url in _HREF.findall(html):
        if url in vistos:
            continue
        vistos.add(url)
        if "/dsas/ca/" in url:
            links.semestrais.append(url)
        elif "/qus/" in url:
            if _tipo(url.rsplit("/", 1)[-1]):
                links.ultimas_semanas.append(url)
        elif "/dsan/" in url:
            achado = _MENSAL.search(url)
            if not achado:
                continue
            nome = achado.group(2)
            tipo, mes = _tipo(nome), _mes(nome)
            if tipo and mes:
                links.mensais.append(LinkMensal(url, int(achado.group(1)), mes, tipo))
    links.semestrais.sort()
    links.mensais.sort(key=lambda m: (m.ano, m.mes, m.tipo))
    links.ultimas_semanas.sort()
    return links
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_links.py -v`
Esperado: 4 passed.

- [ ] **Passo 5: Commit**

```bash
git add pipeline/src/anp/links.py pipeline/tests/test_links.py
git commit -m "feat(pipeline): descoberta de links na página da ANP" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Download com retomada

**Arquivos:**
- Criar: `pipeline/tests/helpers.py` (usado por todas as tarefas seguintes)
- Criar: `pipeline/src/anp/collect.py`
- Criar: `pipeline/tests/test_collect.py`

**Interfaces:**
- Produz:
  - `DownloadError(RuntimeError)`.
  - `nome_local(url: str) -> str`, que converte o caminho depois de `/shpc/` trocando `/` por `_`.
  - `fetch_text(url, session, *, timeout=60, tentativas=3, sleep=time.sleep) -> str`.
  - `download(url, destino_dir: Path, session, *, forcar=False, tentativas=5, timeout=60, sleep=time.sleep) -> Path`.
  - Em `tests/helpers.py`: `FakeResponse`, `FakeSession`, `CABECALHO`, `linha()`, `csv_anp()`, `coletas()` e `diario_sintetico()`.

- [ ] **Passo 1: Criar os helpers de teste**

`pipeline/tests/helpers.py`:

```python
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
```

- [ ] **Passo 2: Escrever o teste que falha**

`pipeline/tests/test_collect.py`:

```python
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
```

- [ ] **Passo 3: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_collect.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.collect'`.

- [ ] **Passo 4: Implementar `collect.py`**

```python
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
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_collect.py -v`
Esperado: 9 passed.

- [ ] **Passo 6: Commit**

```bash
git add pipeline/src/anp/collect.py pipeline/tests/helpers.py pipeline/tests/test_collect.py
git commit -m "feat(pipeline): download com retomada e verificação de tamanho" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Leitura e limpeza dos CSVs

**Arquivos:**
- Criar: `pipeline/src/anp/clean.py`
- Criar: `pipeline/tests/test_clean.py`

**Interfaces:**
- Consome: `anp.config.PRODUTOS`, `UFS`, `PRECO_MIN`, `PRECO_MAX`. Nos testes, `helpers.csv_anp`, `linha` e `coletas`.
- Produz:
  - `SchemaError(ValueError)`.
  - `load_raw(path: Path) -> pd.DataFrame`, com as colunas `cnpj, uf, produto, data, preco`, todas `str`. Aceita ZIP com um único CSV dentro e CSV em UTF-8 ou latin-1.
  - `clean(raw) -> pd.DataFrame`, com as colunas `data` (datetime), `uf`, `produto` (`gasolina|etanol|diesel_s10`) e `preco` (float).

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_clean.py`:

```python
import zipfile

import pandas as pd
import pytest
from helpers import CABECALHO, coletas, csv_anp, linha

from anp.clean import SchemaError, clean, load_raw


def _gravar(tmp_path, nome, conteudo: bytes):
    caminho = tmp_path / nome
    caminho.write_bytes(conteudo)
    return caminho


def test_load_raw_utf8_com_bom(tmp_path):
    p = _gravar(tmp_path, "a.csv", csv_anp([linha("DF", "GASOLINA", "02/01/2026", "6,19")]))
    df = load_raw(p)
    assert list(df.columns) == ["cnpj", "uf", "produto", "data", "preco"]
    assert df.iloc[0].to_dict() == {
        "cnpj": " 00.000.000/0001-00", "uf": "DF", "produto": "GASOLINA",
        "data": "02/01/2026", "preco": "6,19",
    }


def test_load_raw_latin1_com_acentos(tmp_path):
    conteudo = csv_anp([linha("CE", "GASOLINA", "01/07/2021", "5,499", revenda="COMERCIAL DE PETRÓLEO LTDA.")],
                       encoding="latin-1")
    df = load_raw(_gravar(tmp_path, "b.csv", conteudo))
    assert df.iloc[0]["uf"] == "CE"
    assert df.iloc[0]["preco"] == "5,499"


def test_load_raw_zip_sem_extensao_no_nome(tmp_path):
    zip_path = tmp_path / "dsan_2026_04-dados-abertos-precos-diesel-gnv"
    with zipfile.ZipFile(zip_path, "w") as z:
        z.writestr("Preços semestrais - AUTOMOTIVOS_2026.01.csv",
                   csv_anp([linha("AC", "DIESEL S10", "02/01/2026", "7,99")]))
    df = load_raw(zip_path)
    assert df.iloc[0]["produto"] == "DIESEL S10"


def test_load_raw_campo_entre_aspas_com_ponto_e_virgula(tmp_path):
    p = _gravar(tmp_path, "c.csv", csv_anp([linha("SP", "ETANOL", "05/01/2026", "3,99", revenda='"POSTO; TESTE"')]))
    df = load_raw(p)
    assert df.iloc[0]["produto"] == "ETANOL"
    assert df.iloc[0]["preco"] == "3,99"


def test_load_raw_coluna_ausente_explica_o_problema(tmp_path):
    cabecalho_sem_preco = CABECALHO.replace(";Valor de Venda", "")
    p = _gravar(tmp_path, "d.csv", (cabecalho_sem_preco + "\r\n").encode("utf-8-sig"))
    with pytest.raises(SchemaError) as erro:
        load_raw(p)
    assert "Valor de Venda" in str(erro.value)
    assert "Encontradas" in str(erro.value)


def test_clean_mantem_so_os_tres_produtos_e_converte_tipos(tmp_path):
    linhas = coletas("12/01/2026", produtos=("GASOLINA", "ETANOL", "DIESEL S10", "GASOLINA ADITIVADA", "DIESEL", "GNV"),
                     ufs=["DF"])
    df = clean(load_raw(_gravar(tmp_path, "e.csv", csv_anp(linhas))))
    assert sorted(df["produto"]) == ["diesel_s10", "etanol", "gasolina"]
    assert df["data"].iloc[0] == pd.Timestamp("2026-01-12")
    assert df.set_index("produto")["preco"].to_dict() == {"gasolina": 5.0, "etanol": 3.5, "diesel_s10": 6.0}


def test_clean_remove_precos_fora_da_faixa_ufs_invalidas_e_datas_invalidas(tmp_path):
    linhas = [
        linha("DF", "GASOLINA", "12/01/2026", "0,49", cnpj="1"),
        linha("DF", "GASOLINA", "12/01/2026", "0,50", cnpj="2"),
        linha("DF", "GASOLINA", "12/01/2026", "20,00", cnpj="3"),
        linha("DF", "GASOLINA", "12/01/2026", "20,01", cnpj="4"),
        linha("XX", "GASOLINA", "12/01/2026", "6,00", cnpj="5"),
        linha("DF", "GASOLINA", "31/02/2026", "6,00", cnpj="6"),
        linha("DF", "GASOLINA", "12/01/2026", "abc", cnpj="7"),
    ]
    df = clean(load_raw(_gravar(tmp_path, "f.csv", csv_anp(linhas))))
    assert sorted(df["preco"]) == [0.50, 20.00]


def test_clean_remove_duplicata_do_mesmo_posto_mas_mantem_postos_diferentes(tmp_path):
    linhas = [
        linha("DF", "GASOLINA", "12/01/2026", "6,00", cnpj="11.111.111/0001-11"),
        linha("DF", "GASOLINA", "12/01/2026", "6,00", cnpj="11.111.111/0001-11"),
        linha("DF", "GASOLINA", "12/01/2026", "6,00", cnpj="22.222.222/0001-22"),
    ]
    df = clean(load_raw(_gravar(tmp_path, "g.csv", csv_anp(linhas))))
    assert len(df) == 2
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_clean.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.clean'`.

- [ ] **Passo 3: Implementar `clean.py`**

```python
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
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_clean.py -v`
Esperado: 8 passed.

- [ ] **Passo 5: Commit**

```bash
git add pipeline/src/anp/clean.py pipeline/tests/test_clean.py
git commit -m "feat(pipeline): leitura (utf-8/latin-1/zip) e limpeza dos CSVs" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Agregações

**Arquivos:**
- Criar: `pipeline/src/anp/aggregate.py`
- Criar: `pipeline/tests/test_aggregate.py`

**Interfaces:**
- Consome: o DataFrame limpo da Tarefa 4 (`data, uf, produto, preco`).
- Produz (todas as médias são ponderadas pelo número de coletas, e a linha `uf == "BR"` usa todas as coletas do país):
  - `daily(limpo) -> DataFrame[data, uf, produto, soma, n]`.
  - `inicio_semana(datas: pd.Series) -> pd.Series`, que devolve a segunda-feira de cada data.
  - `weekly(diario) -> DataFrame[semana, uf, produto, preco_medio, n]`.
  - `monthly(diario) -> DataFrame[mes ("AAAA-MM"), uf, produto, preco_medio, n]`.
  - `window_mean(diario, inicio: pd.Timestamp, fim: pd.Timestamp) -> DataFrame[uf, produto, preco_medio, n]`.
  - `janela_4_semanas(ultima_data: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]`, com início na segunda-feira três semanas antes da semana da última data e fim na última data.

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_aggregate.py`:

```python
import pandas as pd
import pytest

from anp.aggregate import daily, inicio_semana, janela_4_semanas, monthly, weekly, window_mean


def _limpo(linhas):
    return pd.DataFrame(linhas, columns=["data", "uf", "produto", "preco"]).assign(
        data=lambda d: pd.to_datetime(d["data"])
    )


def test_daily_soma_precos_e_conta_coletas():
    limpo = _limpo([
        ("2026-01-12", "DF", "gasolina", 6.0),
        ("2026-01-12", "DF", "gasolina", 6.4),
        ("2026-01-12", "SP", "gasolina", 5.0),
    ])
    d = daily(limpo)
    df_linha = d[(d.uf == "DF")].iloc[0]
    assert df_linha["soma"] == pytest.approx(12.4)
    assert df_linha["n"] == 2
    assert len(d) == 2


def test_media_nacional_usa_todas_as_coletas_e_nao_a_media_das_ufs():
    diario = daily(_limpo([
        ("2026-01-12", "AC", "gasolina", 4.0),
        ("2026-01-12", "AC", "gasolina", 4.0),
        ("2026-01-13", "SP", "gasolina", 7.0),
    ]))
    s = weekly(diario)
    br = s[s.uf == "BR"].iloc[0]
    assert br["preco_medio"] == pytest.approx(5.0)  # (4+4+7)/3, e não (4+7)/2 = 5.5
    assert br["n"] == 3


def test_semana_comeca_na_segunda_feira():
    datas = pd.Series(pd.to_datetime(["2026-07-20", "2026-07-22", "2026-07-26"]))  # seg, qua, dom
    assert list(inicio_semana(datas)) == [pd.Timestamp("2026-07-20")] * 3


def test_weekly_junta_dias_da_mesma_semana():
    diario = daily(_limpo([
        ("2026-06-29", "DF", "etanol", 4.0),  # segunda
        ("2026-07-01", "DF", "etanol", 5.0),  # quarta (outro mês, mesma semana)
    ]))
    s = weekly(diario)
    linha = s[(s.uf == "DF")].iloc[0]
    assert linha["semana"] == pd.Timestamp("2026-06-29")
    assert linha["preco_medio"] == pytest.approx(4.5)


def test_monthly_agrupa_por_mes_de_calendario():
    diario = daily(_limpo([
        ("2026-06-29", "DF", "etanol", 4.0),
        ("2026-07-01", "DF", "etanol", 5.0),
    ]))
    m = monthly(diario)
    df_m = m[m.uf == "DF"].set_index("mes")["preco_medio"].to_dict()
    assert df_m == {"2026-06": pytest.approx(4.0), "2026-07": pytest.approx(5.0)}


def test_window_mean_respeita_limites_inclusivos():
    diario = daily(_limpo([
        ("2026-06-28", "DF", "gasolina", 9.0),
        ("2026-06-29", "DF", "gasolina", 6.0),
        ("2026-07-20", "DF", "gasolina", 7.0),
        ("2026-07-21", "DF", "gasolina", 9.0),
    ]))
    w = window_mean(diario, pd.Timestamp("2026-06-29"), pd.Timestamp("2026-07-20"))
    df_w = w[w.uf == "DF"].iloc[0]
    assert df_w["preco_medio"] == pytest.approx(6.5)
    assert set(w.columns) == {"uf", "produto", "preco_medio", "n"}


def test_window_mean_vazia_nao_quebra():
    diario = daily(_limpo([("2026-07-20", "DF", "gasolina", 7.0)]))
    w = window_mean(diario, pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-31"))
    assert w.empty


def test_janela_4_semanas_a_partir_de_uma_quarta():
    inicio, fim = janela_4_semanas(pd.Timestamp("2026-07-22"))
    assert inicio == pd.Timestamp("2026-06-29")
    assert fim == pd.Timestamp("2026-07-22")
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_aggregate.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.aggregate'`.

- [ ] **Passo 3: Implementar `aggregate.py`**

```python
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
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_aggregate.py -v`
Esperado: 8 passed.

- [ ] **Passo 5: Commit**

```bash
git add pipeline/src/anp/aggregate.py pipeline/tests/test_aggregate.py
git commit -m "feat(pipeline): agregações diária, semanal, mensal e por janela" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Base diária versionada (upsert e armazenamento)

**Arquivos:**
- Criar: `pipeline/src/anp/merge.py`
- Criar: `pipeline/tests/test_merge.py`

**Interfaces:**
- Consome: `daily()` e `weekly()` da Tarefa 5.
- Produz:
  - `COLUNAS_BASE = ["data", "uf", "produto", "soma", "n"]`.
  - `base_vazia() -> DataFrame`.
  - `upsert(base, novo) -> DataFrame`. Para cada par (`data`, `produto`) presente em `novo`, as linhas de `base` são substituídas. A operação é idempotente.
  - `load_base(pasta: Path) -> DataFrame`, que lê `diario_*.csv`.
  - `save_base(df, pasta: Path) -> None`, que grava um `diario_AAAA.csv` por ano, com `soma` em 4 casas decimais e linhas terminadas em `\n`.

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_merge.py`:

```python
import pandas as pd
import pytest

from anp.aggregate import daily, weekly
from anp.merge import COLUNAS_BASE, base_vazia, load_base, save_base, upsert


def _diario(linhas):
    limpo = pd.DataFrame(linhas, columns=["data", "uf", "produto", "preco"]).assign(
        data=lambda d: pd.to_datetime(d["data"])
    )
    return daily(limpo)


def test_upsert_em_base_vazia():
    novo = _diario([("2026-07-20", "DF", "gasolina", 6.0)])
    out = upsert(base_vazia(), novo)
    assert list(out.columns) == COLUNAS_BASE
    assert len(out) == 1


def test_upsert_substitui_mesma_data_e_produto():
    base = _diario([("2026-07-20", "DF", "gasolina", 6.0), ("2026-07-20", "SP", "gasolina", 5.0)])
    novo = _diario([("2026-07-20", "DF", "gasolina", 6.5)])  # revisão da ANP, só DF
    out = upsert(base, novo)
    assert len(out) == 1  # a data inteira daquele produto vem do arquivo novo
    assert out.iloc[0]["soma"] == pytest.approx(6.5)


def test_upsert_nao_apaga_outro_produto_na_mesma_data():
    diesel = _diario([("2026-07-20", "DF", "diesel_s10", 7.0)])
    gasolina_etanol = _diario([("2026-07-20", "DF", "gasolina", 6.0), ("2026-07-20", "DF", "etanol", 4.0)])
    out = upsert(diesel, gasolina_etanol)
    assert sorted(out["produto"]) == ["diesel_s10", "etanol", "gasolina"]


def test_semana_dividida_entre_dois_arquivos_fica_completa():
    semestral = _diario([("2026-06-29", "DF", "gasolina", 6.0), ("2026-06-30", "DF", "gasolina", 6.0)])
    mensal_julho = _diario([("2026-07-01", "DF", "gasolina", 9.0)])
    base = upsert(upsert(base_vazia(), semestral), mensal_julho)
    s = weekly(base)
    linha = s[(s.uf == "DF") & (s.semana == pd.Timestamp("2026-06-29"))].iloc[0]
    assert linha["preco_medio"] == pytest.approx(7.0)  # (6+6+9)/3
    assert linha["n"] == 3


def test_upsert_idempotente():
    base = _diario([("2026-07-13", "DF", "gasolina", 6.0)])
    novo = _diario([("2026-07-13", "DF", "gasolina", 6.1), ("2026-07-20", "DF", "gasolina", 6.2)])
    uma_vez = upsert(base, novo)
    duas_vezes = upsert(uma_vez, novo)
    pd.testing.assert_frame_equal(uma_vez, duas_vezes)


def test_save_e_load_particionado_por_ano(tmp_path):
    base = _diario([
        ("2025-12-29", "DF", "gasolina", 6.123456),
        ("2026-01-05", "DF", "gasolina", 6.2),
    ])
    save_base(base, tmp_path)
    assert sorted(p.name for p in tmp_path.glob("diario_*.csv")) == ["diario_2025.csv", "diario_2026.csv"]
    assert (tmp_path / "diario_2025.csv").read_text(encoding="utf-8") == (
        "data,uf,produto,soma,n\n2025-12-29,DF,gasolina,6.1235,1\n"
    )
    lida = load_base(tmp_path)
    assert list(lida.columns) == COLUNAS_BASE
    assert lida["data"].tolist() == [pd.Timestamp("2025-12-29"), pd.Timestamp("2026-01-05")]
    assert lida["n"].tolist() == [1, 1]


def test_load_base_de_pasta_vazia(tmp_path):
    assert load_base(tmp_path).empty
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_merge.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.merge'`.

- [ ] **Passo 3: Implementar `merge.py`**

```python
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
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_merge.py -v`
Esperado: 7 passed.

- [ ] **Passo 5: Commit**

```bash
git add pipeline/src/anp/merge.py pipeline/tests/test_merge.py
git commit -m "feat(pipeline): base diária com upsert por data e produto" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: IPCA e correção pela inflação

**Arquivos:**
- Criar: `pipeline/src/anp/ipca.py`
- Criar: `pipeline/tests/test_ipca.py`

**Interfaces:**
- Consome: `anp.config.BCB_IPCA_URL` e `USER_AGENT`. Nos testes, `helpers.FakeSession` e `FakeResponse`.
- Produz:
  - `parse_ipca(payload: list[dict]) -> DataFrame[mes ("AAAA-MM"), variacao (float, %)]`.
  - `get_ipca(session, cache: Path, timeout=30) -> tuple[DataFrame, bool]`. O booleano é `True` quando o resultado veio do cache.
  - `fatores(ipca) -> tuple[pd.Series, str]`. A série vai de mês para fator, e a string é o mês de referência.
  - `aplicar_real(mensal, fator, ref) -> DataFrame`, que acrescenta a coluna `real`. Para meses posteriores a `ref`, `real` é igual a `preco_medio`. Para meses sem IPCA anteriores ao início da série, `real` é NaN.

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_ipca.py`:

```python
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
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_ipca.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.ipca'`.

- [ ] **Passo 3: Implementar `ipca.py`**

```python
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
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_ipca.py -v`
Esperado: 7 passed.

- [ ] **Passo 5: Commit**

```bash
git add pipeline/src/anp/ipca.py pipeline/tests/test_ipca.py
git commit -m "feat(pipeline): IPCA do BCB com cache e fatores de correção" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Validações de sanidade

**Arquivos:**
- Criar: `pipeline/src/anp/validate.py`
- Criar: `pipeline/tests/test_validate.py`

**Interfaces:**
- Consome: `weekly()` da Tarefa 5, `helpers.diario_sintetico` e as constantes de `config`.
- Produz:
  - `ValidationError(RuntimeError)`, com o atributo `erros: list[str]`.
  - `validate(diario, maximo_anterior: pd.Timestamp | None, hoje: datetime.date) -> None`. Levanta `ValidationError` listando **todos** os problemas encontrados.

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_validate.py`:

```python
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
    assert len(erro.value.erros) == 2  # data futura + AC ausente
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_validate.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.validate'`.

- [ ] **Passo 3: Implementar `validate.py`**

```python
"""Checagens de sanidade: nenhum dado é publicado se alguma delas falhar."""

from datetime import date

import pandas as pd

from anp.aggregate import weekly
from anp.config import MAX_VARIACAO_SEMANAL, PRECO_MAX, PRECO_MIN, UFS


class ValidationError(RuntimeError):
    def __init__(self, erros: list[str]):
        super().__init__("Validação falhou:\n- " + "\n- ".join(erros))
        self.erros = erros


def validate(diario: pd.DataFrame, maximo_anterior: pd.Timestamp | None, hoje: date) -> None:
    if diario.empty:
        raise ValidationError(["base vazia"])
    erros: list[str] = []

    medias = diario["soma"] / diario["n"]
    fora = int((~medias.between(PRECO_MIN, PRECO_MAX)).sum())
    if fora:
        erros.append(f"{fora} médias diárias fora da faixa de R$ {PRECO_MIN:.2f} a R$ {PRECO_MAX:.2f}")

    ultima = diario["data"].max()
    if ultima.normalize() > pd.Timestamp(hoje):
        erros.append(f"data futura na base: {ultima.date()}")
    if maximo_anterior is not None and ultima < maximo_anterior:
        erros.append(f"última data {ultima.date()} é anterior à que já estava na base ({maximo_anterior.date()})")

    semanal = weekly(diario)
    ultima_semana = semanal["semana"].max()
    presentes = set(
        semanal[(semanal.semana == ultima_semana) & (semanal.produto == "gasolina") & (semanal.uf != "BR")]["uf"]
    )
    faltando = sorted(set(UFS) - presentes)
    if faltando:
        erros.append(f"semana de {ultima_semana.date()} sem gasolina para: {', '.join(faltando)}")

    br = semanal[(semanal.uf == "BR") & (semanal.produto == "gasolina")].sort_values("semana")
    if len(br) >= 2:
        anterior, atual = br["preco_medio"].iloc[-2], br["preco_medio"].iloc[-1]
        variacao = abs(atual / anterior - 1)
        if variacao >= MAX_VARIACAO_SEMANAL - 1e-9:
            erros.append(f"gasolina BR variou {variacao:.1%} em uma semana (limite {MAX_VARIACAO_SEMANAL:.0%})")

    if erros:
        raise ValidationError(erros)
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_validate.py -v`
Esperado: 9 passed.

- [ ] **Passo 5: Commit**

```bash
git add pipeline/src/anp/validate.py pipeline/tests/test_validate.py
git commit -m "feat(pipeline): validações de sanidade antes de publicar" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Contrato (JSON Schemas) e exportação

**Arquivos:**
- Criar: `schemas/evolucao.schema.json`
- Criar: `schemas/ranking_uf.schema.json`
- Criar: `schemas/etanol_gasolina.schema.json`
- Criar: `schemas/meta.schema.json`
- Criar: `pipeline/src/anp/export.py`
- Criar: `pipeline/tests/test_export.py`

**Interfaces:**
- Consome: `monthly`, `window_mean` e `janela_4_semanas` (Tarefa 5); `fatores` e `aplicar_real` (Tarefa 7); as constantes de `config`.
- Produz:
  - `ARQUIVOS = ("evolucao", "ranking_uf", "etanol_gasolina", "meta")`.
  - `build_evolucao(mensal_com_real, ipca_ref) -> dict`.
  - `build_ranking(diario) -> dict`.
  - `build_etanol_gasolina(ranking, mensal) -> dict`.
  - `build_meta(diario, ranking, etanol_gasolina, evolucao, ipca_ref, ipca_em_cache, agora: datetime) -> dict`.
  - `export_all(diario, ipca_df, ipca_em_cache, out_dir, schemas_dir, agora) -> dict[str, dict]`. Valida os 4 objetos antes de gravar qualquer arquivo.
  - Os formatos exatos estão nos schemas deste passo. A Parte 2 (site) consome estes mesmos schemas.

- [ ] **Passo 1: Criar os schemas**

`schemas/evolucao.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "evolucao.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["meses", "ipca_ref", "series"],
  "properties": {
    "meses": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/mes" } },
    "ipca_ref": { "$ref": "#/$defs/mes" },
    "series": {
      "type": "object",
      "propertyNames": { "pattern": "^[A-Z]{2}$" },
      "additionalProperties": {
        "type": "object",
        "propertyNames": { "enum": ["gasolina", "etanol", "diesel_s10"] },
        "additionalProperties": {
          "type": "object",
          "additionalProperties": false,
          "required": ["nominal", "real"],
          "properties": {
            "nominal": { "$ref": "#/$defs/serie" },
            "real": { "$ref": "#/$defs/serie" }
          }
        }
      }
    }
  },
  "$defs": {
    "mes": { "type": "string", "pattern": "^\\d{4}-\\d{2}$" },
    "serie": { "type": "array", "items": { "type": ["number", "null"] } }
  }
}
```

`schemas/ranking_uf.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ranking_uf.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["periodo", "itens"],
  "properties": {
    "periodo": {
      "type": "object",
      "additionalProperties": false,
      "required": ["inicio", "fim"],
      "properties": {
        "inicio": { "$ref": "#/$defs/data" },
        "fim": { "$ref": "#/$defs/data" }
      }
    },
    "itens": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["uf", "produto", "preco_medio", "variacao_12m_pct", "n_coletas"],
        "properties": {
          "uf": { "type": "string", "pattern": "^[A-Z]{2}$" },
          "produto": { "enum": ["gasolina", "etanol", "diesel_s10"] },
          "preco_medio": { "type": "number" },
          "variacao_12m_pct": { "type": ["number", "null"] },
          "n_coletas": { "type": "integer", "minimum": 1 }
        }
      }
    }
  },
  "$defs": {
    "data": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" }
  }
}
```

`schemas/etanol_gasolina.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "etanol_gasolina.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["limiar", "atual", "historico"],
  "properties": {
    "limiar": { "type": "number" },
    "atual": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["uf", "razao", "compensa"],
        "properties": {
          "uf": { "type": "string", "pattern": "^[A-Z]{2}$" },
          "razao": { "type": "number" },
          "compensa": { "enum": ["etanol", "gasolina"] }
        }
      }
    },
    "historico": {
      "type": "object",
      "additionalProperties": false,
      "required": ["meses", "razao"],
      "properties": {
        "meses": { "type": "array", "items": { "type": "string", "pattern": "^\\d{4}-\\d{2}$" } },
        "razao": {
          "type": "object",
          "propertyNames": { "pattern": "^[A-Z]{2}$" },
          "additionalProperties": { "type": "array", "items": { "type": ["number", "null"] } }
        }
      }
    }
  }
}
```

`schemas/meta.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "meta.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["atualizado_em", "semana_mais_recente", "n_coletas_total", "ipca_ate", "ipca_em_cache", "fontes", "destaques", "serie_home"],
  "properties": {
    "atualizado_em": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$" },
    "semana_mais_recente": { "$ref": "#/$defs/data" },
    "n_coletas_total": { "type": "integer", "minimum": 1 },
    "ipca_ate": { "$ref": "#/$defs/mes" },
    "ipca_em_cache": { "type": "boolean" },
    "fontes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["nome", "url"],
        "properties": {
          "nome": { "type": "string" },
          "url": { "type": "string", "pattern": "^https://" }
        }
      }
    },
    "destaques": {
      "type": "object",
      "additionalProperties": false,
      "required": ["gasolina_df", "gasolina_br", "diff_df_br_pct", "ufs_etanol_compensa", "maior_alta_12m"],
      "properties": {
        "gasolina_df": { "type": "number" },
        "gasolina_br": { "type": "number" },
        "diff_df_br_pct": { "type": ["number", "null"] },
        "ufs_etanol_compensa": { "type": "integer", "minimum": 0, "maximum": 27 },
        "maior_alta_12m": {
          "oneOf": [
            { "type": "null" },
            {
              "type": "object",
              "additionalProperties": false,
              "required": ["uf", "produto", "pct"],
              "properties": {
                "uf": { "type": "string", "pattern": "^[A-Z]{2}$" },
                "produto": { "enum": ["gasolina", "etanol", "diesel_s10"] },
                "pct": { "type": "number" }
              }
            }
          ]
        }
      }
    },
    "serie_home": {
      "type": "object",
      "additionalProperties": false,
      "required": ["meses", "gasolina_br", "gasolina_df"],
      "properties": {
        "meses": { "type": "array", "items": { "$ref": "#/$defs/mes" } },
        "gasolina_br": { "$ref": "#/$defs/serie" },
        "gasolina_df": { "$ref": "#/$defs/serie" }
      }
    }
  },
  "$defs": {
    "data": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
    "mes": { "type": "string", "pattern": "^\\d{4}-\\d{2}$" },
    "serie": { "type": "array", "items": { "type": ["number", "null"] } }
  }
}
```

- [ ] **Passo 2: Escrever o teste que falha**

`pipeline/tests/test_export.py`:

```python
import json
import shutil
from datetime import datetime, timezone

import jsonschema
import pandas as pd
import pytest
from helpers import diario_sintetico

from anp.aggregate import monthly
from anp.config import SCHEMAS_DIR, UFS
from anp.export import (
    ARQUIVOS,
    build_etanol_gasolina,
    build_evolucao,
    build_meta,
    build_ranking,
    export_all,
)
from anp.ipca import aplicar_real, fatores, parse_ipca

AGORA = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)
# segundas-feiras de 30/06/2025 a 20/07/2026 (56 semanas)
DATAS = pd.date_range("2025-06-30", "2026-07-20", freq="7D").strftime("%Y-%m-%d").tolist()


def _preco(d, uf, p):
    if p == "gasolina":
        if uf == "DF":
            return 7.2 if d >= pd.Timestamp("2026-06-29") else 6.0  # +20% na janela atual
        return 5.0
    if p == "etanol":
        return 3.0 if uf == "SP" else 3.5
    return 6.0


def _ipca():
    meses = pd.period_range("2025-06", "2026-06", freq="M")
    return parse_ipca([{"data": f"01/{m.month:02d}/{m.year}", "valor": "0.5"} for m in meses])


@pytest.fixture
def diario():
    return diario_sintetico(DATAS, preco=_preco)


@pytest.fixture
def mensal(diario):
    fator, ref = fatores(_ipca())
    return aplicar_real(monthly(diario), fator, ref)


def test_evolucao_meses_continuos_e_series_alinhadas(mensal):
    evo = build_evolucao(mensal, "2026-06")
    assert evo["meses"][0] == "2025-06" and evo["meses"][-1] == "2026-07"
    assert len(evo["meses"]) == 14
    assert set(evo["series"]) == {"BR", *UFS}
    for produtos in evo["series"].values():
        for serie in produtos.values():
            assert len(serie["nominal"]) == len(serie["real"]) == 14
    br_gas = evo["series"]["BR"]["gasolina"]
    idx_ref = evo["meses"].index("2026-06")
    assert br_gas["real"][idx_ref] == br_gas["nominal"][idx_ref]
    assert br_gas["real"][-1] == br_gas["nominal"][-1]  # mês depois do último IPCA
    assert br_gas["real"][0] > br_gas["nominal"][0]  # valor antigo corrigido para cima


def test_ranking_janela_e_variacao_12_meses(diario):
    r = build_ranking(diario)
    assert r["periodo"] == {"inicio": "2026-06-29", "fim": "2026-07-20"}
    itens = {(i["uf"], i["produto"]): i for i in r["itens"]}
    assert itens[("DF", "gasolina")]["preco_medio"] == pytest.approx(7.2)
    assert itens[("DF", "gasolina")]["variacao_12m_pct"] == pytest.approx(20.0)
    assert itens[("SP", "gasolina")]["variacao_12m_pct"] == pytest.approx(0.0)
    assert ("BR", "gasolina") in itens
    assert itens[("DF", "gasolina")]["n_coletas"] == 40  # 4 semanas × 10 coletas


def test_etanol_gasolina_compensa_abaixo_de_70(diario, mensal):
    ranking = build_ranking(diario)
    eg = build_etanol_gasolina(ranking, mensal)
    atual = {a["uf"]: a for a in eg["atual"]}
    assert atual["SP"] == {"uf": "SP", "razao": 0.6, "compensa": "etanol"}
    assert atual["RJ"]["razao"] == 0.7 and atual["RJ"]["compensa"] == "gasolina"  # 0,70 não é "abaixo"
    assert eg["limiar"] == 0.7
    assert len(eg["historico"]["razao"]["SP"]) == len(eg["historico"]["meses"])


def test_meta_destaques(diario, mensal):
    ranking = build_ranking(diario)
    eg = build_etanol_gasolina(ranking, mensal)
    evo = build_evolucao(mensal, "2026-06")
    meta = build_meta(diario, ranking, eg, evo, "2026-06", False, AGORA)
    assert meta["atualizado_em"] == "2026-07-25T12:00:00Z"
    assert meta["semana_mais_recente"] == "2026-07-20"
    assert meta["destaques"]["gasolina_df"] == pytest.approx(7.2)
    assert meta["destaques"]["ufs_etanol_compensa"] == 2  # SP (3,0/5,0) e DF (3,5/7,2)
    assert meta["destaques"]["maior_alta_12m"] == {"uf": "DF", "produto": "gasolina", "pct": 20.0}
    assert len(meta["serie_home"]["meses"]) == 14  # menos de 24 meses disponíveis
    assert len(meta["serie_home"]["gasolina_df"]) == 14


def test_export_all_grava_quatro_arquivos_validos(diario, tmp_path):
    saidas = export_all(diario, _ipca(), False, tmp_path, SCHEMAS_DIR, AGORA)
    assert sorted(p.name for p in tmp_path.iterdir()) == sorted(f"{n}.json" for n in ARQUIVOS)
    for nome in ARQUIVOS:
        esquema = json.loads((SCHEMAS_DIR / f"{nome}.schema.json").read_text(encoding="utf-8"))
        conteudo = json.loads((tmp_path / f"{nome}.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(esquema).validate(conteudo)
        assert conteudo == saidas[nome]


def test_export_all_nao_grava_nada_se_um_schema_falhar(diario, tmp_path):
    schemas = tmp_path / "schemas"
    shutil.copytree(SCHEMAS_DIR, schemas)
    meta_schema = json.loads((schemas / "meta.schema.json").read_text(encoding="utf-8"))
    meta_schema["required"].append("campo_que_nao_existe")
    (schemas / "meta.schema.json").write_text(json.dumps(meta_schema), encoding="utf-8")
    saida = tmp_path / "out"
    with pytest.raises(jsonschema.ValidationError):
        export_all(diario, _ipca(), False, saida, schemas, AGORA)
    assert not saida.exists() or not any(saida.iterdir())
```

- [ ] **Passo 3: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_export.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.export'`.

- [ ] **Passo 4: Implementar `export.py`**

```python
"""Monta, valida e grava os JSONs consumidos pelo site."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from jsonschema import Draft202012Validator

from anp.aggregate import janela_4_semanas, monthly, window_mean
from anp.config import ANP_PAGE_URL, BCB_IPCA_URL, LIMIAR_ETANOL, ORDEM_PRODUTOS, UFS
from anp.ipca import aplicar_real, fatores

ARQUIVOS = ("evolucao", "ranking_uf", "etanol_gasolina", "meta")
REGIOES = ["BR", *UFS]
UM_ANO = pd.Timedelta(days=364)


def _num(valor, casas: int = 3):
    return None if valor is None or pd.isna(valor) else round(float(valor), casas)


def _todos_meses(inicio: str, fim: str) -> list[str]:
    return [p.strftime("%Y-%m") for p in pd.period_range(inicio, fim, freq="M")]


def build_evolucao(mensal: pd.DataFrame, ipca_ref: str) -> dict:
    meses = _todos_meses(mensal["mes"].min(), mensal["mes"].max())
    series: dict[str, dict] = {}
    for regiao in REGIOES:
        por_produto = {}
        for produto in ORDEM_PRODUTOS:
            recorte = mensal[(mensal["uf"] == regiao) & (mensal["produto"] == produto)]
            if recorte.empty:
                continue
            recorte = recorte.set_index("mes").reindex(meses)
            por_produto[produto] = {
                "nominal": [_num(v) for v in recorte["preco_medio"]],
                "real": [_num(v) for v in recorte["real"]],
            }
        if por_produto:
            series[regiao] = por_produto
    return {"meses": meses, "ipca_ref": ipca_ref, "series": series}


def build_ranking(diario: pd.DataFrame) -> dict:
    inicio, fim = janela_4_semanas(diario["data"].max())
    atual = window_mean(diario, inicio, fim)
    anterior = window_mean(diario, inicio - UM_ANO, fim - UM_ANO).set_index(["uf", "produto"])["preco_medio"]
    itens = []
    for linha in atual.itertuples():
        preco_antes = anterior.get((linha.uf, linha.produto))
        variacao = None if preco_antes is None or pd.isna(preco_antes) else (linha.preco_medio / preco_antes - 1) * 100
        itens.append({
            "uf": linha.uf,
            "produto": linha.produto,
            "preco_medio": _num(linha.preco_medio),
            "variacao_12m_pct": _num(variacao, 1),
            "n_coletas": int(linha.n),
        })
    return {"periodo": {"inicio": inicio.strftime("%Y-%m-%d"), "fim": fim.strftime("%Y-%m-%d")}, "itens": itens}


def build_etanol_gasolina(ranking: dict, mensal: pd.DataFrame) -> dict:
    precos = {(i["uf"], i["produto"]): i["preco_medio"] for i in ranking["itens"]}
    atual = []
    for uf in REGIOES:
        etanol, gasolina = precos.get((uf, "etanol")), precos.get((uf, "gasolina"))
        if etanol is None or gasolina is None:
            continue
        razao = round(etanol / gasolina, 3)
        atual.append({"uf": uf, "razao": razao, "compensa": "etanol" if razao < LIMIAR_ETANOL else "gasolina"})

    tabela = mensal.pivot_table(index=["mes", "uf"], columns="produto", values="preco_medio")
    razao_mensal = (tabela["etanol"] / tabela["gasolina"]).rename("razao").reset_index()
    meses = _todos_meses(mensal["mes"].min(), mensal["mes"].max())
    historico = {}
    for uf in REGIOES:
        serie = razao_mensal[razao_mensal["uf"] == uf].set_index("mes")["razao"].reindex(meses)
        if serie.notna().any():
            historico[uf] = [_num(v) for v in serie]
    return {"limiar": LIMIAR_ETANOL, "atual": atual, "historico": {"meses": meses, "razao": historico}}


def build_meta(diario: pd.DataFrame, ranking: dict, etanol_gasolina: dict, evolucao: dict,
               ipca_ref: str, ipca_em_cache: bool, agora: datetime) -> dict:
    itens = {(i["uf"], i["produto"]): i for i in ranking["itens"]}
    gasolina_df = itens[("DF", "gasolina")]["preco_medio"]
    gasolina_br = itens[("BR", "gasolina")]["preco_medio"]
    altas = [i for i in ranking["itens"] if i["uf"] != "BR" and i["variacao_12m_pct"] is not None]
    maior = max(altas, key=lambda i: i["variacao_12m_pct"], default=None)
    ultima = diario["data"].max()
    semana = ultima - pd.Timedelta(days=ultima.dayofweek)
    vazio = [None] * len(evolucao["meses"])

    def serie_gasolina(uf: str) -> list:
        return evolucao["series"].get(uf, {}).get("gasolina", {}).get("nominal", vazio)[-24:]

    return {
        "atualizado_em": agora.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "semana_mais_recente": semana.strftime("%Y-%m-%d"),
        "n_coletas_total": int(diario["n"].sum()),
        "ipca_ate": ipca_ref,
        "ipca_em_cache": ipca_em_cache,
        "fontes": [
            {"nome": "ANP — Série Histórica de Preços de Combustíveis", "url": ANP_PAGE_URL},
            {"nome": "Banco Central — SGS 433 (IPCA)", "url": BCB_IPCA_URL},
        ],
        "destaques": {
            "gasolina_df": gasolina_df,
            "gasolina_br": gasolina_br,
            "diff_df_br_pct": _num((gasolina_df / gasolina_br - 1) * 100, 1),
            "ufs_etanol_compensa": sum(
                1 for a in etanol_gasolina["atual"] if a["uf"] != "BR" and a["compensa"] == "etanol"
            ),
            "maior_alta_12m": None if maior is None else {
                "uf": maior["uf"], "produto": maior["produto"], "pct": maior["variacao_12m_pct"],
            },
        },
        "serie_home": {
            "meses": evolucao["meses"][-24:],
            "gasolina_br": serie_gasolina("BR"),
            "gasolina_df": serie_gasolina("DF"),
        },
    }


def _validador(schemas_dir: Path, nome: str) -> Draft202012Validator:
    esquema = json.loads((schemas_dir / f"{nome}.schema.json").read_text(encoding="utf-8"))
    return Draft202012Validator(esquema)


def export_all(diario: pd.DataFrame, ipca_df: pd.DataFrame, ipca_em_cache: bool, out_dir: Path,
               schemas_dir: Path, agora: datetime) -> dict[str, dict]:
    fator, ref = fatores(ipca_df)
    mensal = aplicar_real(monthly(diario), fator, ref)
    evolucao = build_evolucao(mensal, ref)
    ranking = build_ranking(diario)
    etanol_gasolina = build_etanol_gasolina(ranking, mensal)
    meta = build_meta(diario, ranking, etanol_gasolina, evolucao, ref, ipca_em_cache, agora)
    saidas = {"evolucao": evolucao, "ranking_uf": ranking, "etanol_gasolina": etanol_gasolina, "meta": meta}

    for nome, obj in saidas.items():
        _validador(schemas_dir, nome).validate(obj)

    out_dir.mkdir(parents=True, exist_ok=True)
    for nome, obj in saidas.items():
        (out_dir / f"{nome}.json").write_text(
            json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    return saidas
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_export.py -v`
Esperado: 6 passed.

- [ ] **Passo 6: Rodar a suíte inteira**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest -q`
Esperado: todos os testes passam, sem nenhuma falha.

- [ ] **Passo 7: Commit**

```bash
git add schemas pipeline/src/anp/export.py pipeline/tests/test_export.py
git commit -m "feat(pipeline): JSON Schemas do contrato e exportação validada" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Linha de comando (`anp backfill` / `anp update`)

**Arquivos:**
- Criar: `pipeline/src/anp/cli.py`
- Criar: `pipeline/tests/test_cli.py`

**Interfaces:**
- Consome: todos os módulos anteriores.
- Produz:
  - `executar(modo: str, *, session, raw_dir, processed_dir, out_dir, schemas_dir, agora: datetime, apagar_brutos: bool = False) -> None`.
  - `main(argv: list[str] | None = None) -> int`, exposto como o comando `anp` pelo `pyproject.toml`. Devolve 0 em caso de sucesso e 1 em caso de erro, com a mensagem `ERRO: ...` no stderr.
- A ordem é garantida: coletar → validar → exportar (com validação dos schemas) → `save_base`. Se qualquer etapa falhar, nem `site/public/data/` nem `diario_*.csv` são gravados.

- [ ] **Passo 1: Escrever o teste que falha**

`pipeline/tests/test_cli.py`:

```python
import json
from datetime import datetime, timezone

import pytest
from helpers import FakeResponse, FakeSession, coletas, csv_anp

from anp.cli import executar, main
from anp.config import SCHEMAS_DIR
from anp.validate import ValidationError

PAGINA = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis"
B = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc"
SEMESTRAL = f"{B}/dsas/ca/ca-2026-01.csv"
MENSAL_JUN = f"{B}/dsan/2026/06-dados-abertos-precos-2026-06-gasolina-etanol.csv"
MENSAL_JUL_GE = f"{B}/dsan/2026/07-dados-abertos-precos-gasolina-etanol.csv"
MENSAL_JUL_DG = f"{B}/dsan/2026/07-dados-abertos-precos-diesel-gnv.csv"
QUS_GE = f"{B}/qus/ultimas-4-semanas-gasolina-etanol.csv"
QUS_DG = f"{B}/qus/ultimas-4-semanas-diesel-gnv.csv"
IPCA = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
AGORA = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)

GE = ("GASOLINA", "ETANOL", "GASOLINA ADITIVADA")
DG = ("DIESEL S10", "DIESEL", "GNV")


def _html(*urls):
    return "".join(f'<a href="{u}">x</a>' for u in urls).encode()


def _rotas(qus_ge_linhas=None):
    semestral = coletas("22/06/2026", GE + DG) + coletas("29/06/2026", GE + DG)
    qus_ge = qus_ge_linhas if qus_ge_linhas is not None else coletas("13/07/2026", GE) + coletas("20/07/2026", GE)
    ipca = [{"data": f"01/{m:02d}/2026", "valor": "0.5"} for m in range(1, 7)]
    return {
        PAGINA: FakeResponse(_html(SEMESTRAL, MENSAL_JUN, MENSAL_JUL_GE, MENSAL_JUL_DG, QUS_GE, QUS_DG)),
        SEMESTRAL: FakeResponse(csv_anp(semestral)),
        MENSAL_JUL_GE: FakeResponse(csv_anp(coletas("06/07/2026", GE))),
        MENSAL_JUL_DG: FakeResponse(csv_anp(coletas("06/07/2026", DG))),
        QUS_GE: FakeResponse(csv_anp(qus_ge)),
        QUS_DG: FakeResponse(csv_anp(coletas("13/07/2026", DG) + coletas("20/07/2026", DG))),
        IPCA: FakeResponse(json.dumps(ipca).encode()),
    }


def _dirs(tmp_path):
    return {
        "raw_dir": tmp_path / "raw",
        "processed_dir": tmp_path / "processed",
        "out_dir": tmp_path / "out",
        "schemas_dir": SCHEMAS_DIR,
    }


def test_backfill_gera_base_e_quatro_jsons(tmp_path):
    s = FakeSession(_rotas())
    executar("backfill", session=s, agora=AGORA, **_dirs(tmp_path))
    out = tmp_path / "out"
    assert sorted(p.name for p in out.iterdir()) == [
        "etanol_gasolina.json", "evolucao.json", "meta.json", "ranking_uf.json",
    ]
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8"))
    assert meta["semana_mais_recente"] == "2026-07-20"
    assert meta["destaques"]["gasolina_df"] == 5.0
    assert (tmp_path / "processed" / "diario_2026.csv").exists()
    assert (tmp_path / "processed" / "ipca.csv").exists()
    urls = [u for u, _ in s.chamadas]
    assert MENSAL_JUN not in urls  # junho já veio no semestral


def test_update_com_os_mesmos_dados_nao_altera_a_base(tmp_path):
    executar("backfill", session=FakeSession(_rotas()), agora=AGORA, **_dirs(tmp_path))
    processed = tmp_path / "processed"
    antes = {p.name: p.read_bytes() for p in processed.iterdir()}
    executar("update", session=FakeSession(_rotas()), agora=AGORA, **_dirs(tmp_path))
    depois = {p.name: p.read_bytes() for p in processed.iterdir()}
    assert antes == depois


def test_update_sem_base_pede_backfill(tmp_path):
    with pytest.raises(RuntimeError, match="backfill"):
        executar("update", session=FakeSession(_rotas()), agora=AGORA, **_dirs(tmp_path))


def test_falha_de_validacao_nao_grava_nada(tmp_path):
    sem_df = [l for l in coletas("20/07/2026", GE) if ";DF;" not in l]
    rotas = _rotas(qus_ge_linhas=coletas("13/07/2026", GE) + sem_df)
    with pytest.raises(ValidationError):
        executar("backfill", session=FakeSession(rotas), agora=AGORA, **_dirs(tmp_path))
    assert not (tmp_path / "out").exists()
    assert not list((tmp_path / "processed").glob("diario_*.csv"))


def test_main_devolve_1_e_mensagem_clara_em_erro(tmp_path, capsys, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("ANP fora do ar")
    monkeypatch.setattr("anp.cli.executar", explode)
    codigo = main(["update", "--raw-dir", str(tmp_path)])
    assert codigo == 1
    assert "ERRO: ANP fora do ar" in capsys.readouterr().err
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_cli.py -v`
Esperado: FALHA com `ModuleNotFoundError: No module named 'anp.cli'`.

- [ ] **Passo 3: Implementar `cli.py`**

```python
"""Linha de comando: `anp backfill` (carga histórica, uma vez) e `anp update` (semanal)."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

from anp import config
from anp.aggregate import daily
from anp.clean import clean, load_raw
from anp.collect import download, fetch_text
from anp.export import export_all
from anp.ipca import get_ipca
from anp.links import discover_links
from anp.merge import base_vazia, load_base, save_base, upsert
from anp.validate import validate


def _processar(url: str, base: pd.DataFrame, raw_dir: Path, session, *, forcar: bool = False,
               apagar: bool = False) -> pd.DataFrame:
    caminho = download(url, raw_dir, session, forcar=forcar)
    print(f"  processando {caminho.name}", flush=True)
    novo = daily(clean(load_raw(caminho)))
    if apagar:
        caminho.unlink()
    return upsert(base, novo)


def executar(modo: str, *, session, raw_dir: Path, processed_dir: Path, out_dir: Path, schemas_dir: Path,
             agora: datetime, apagar_brutos: bool = False) -> None:
    links = discover_links(fetch_text(config.ANP_PAGE_URL, session))
    if not links.ultimas_semanas:
        raise RuntimeError("Nenhum link de 'últimas 4 semanas' encontrado na página da ANP")

    if modo == "backfill":
        if not links.semestrais:
            raise RuntimeError("Nenhum arquivo semestral encontrado na página da ANP")
        base = base_vazia()
        maximo_anterior = None
        print(f"Semestrais: {len(links.semestrais)} arquivos", flush=True)
        for url in links.semestrais:
            base = _processar(url, base, raw_dir, session, apagar=apagar_brutos)
        ultima = base["data"].max()
        for mensal in links.mensais:
            if (mensal.ano, mensal.mes) > (ultima.year, ultima.month):
                base = _processar(mensal.url, base, raw_dir, session, apagar=apagar_brutos)
    elif modo == "update":
        base = load_base(processed_dir)
        if base.empty:
            raise RuntimeError(f"Base vazia em {processed_dir}: rode `anp backfill` primeiro")
        maximo_anterior = base["data"].max()
    else:
        raise ValueError(f"modo desconhecido: {modo}")

    for url in links.ultimas_semanas:
        base = _processar(url, base, raw_dir, session, forcar=True)

    validate(base, maximo_anterior, agora.date())
    ipca, ipca_em_cache = get_ipca(session, processed_dir / "ipca.csv")
    export_all(base, ipca, ipca_em_cache, out_dir, schemas_dir, agora)
    save_base(base, processed_dir)
    print(f"OK: {len(base)} linhas na base, última data {base['data'].max().date()}", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="anp", description="Pipeline de preços de combustíveis da ANP")
    parser.add_argument("modo", choices=["backfill", "update"])
    parser.add_argument("--raw-dir", type=Path, default=config.RAW_DIR)
    parser.add_argument("--processed-dir", type=Path, default=config.PROCESSED_DIR)
    parser.add_argument("--out-dir", type=Path, default=config.OUT_DIR)
    parser.add_argument("--schemas-dir", type=Path, default=config.SCHEMAS_DIR)
    parser.add_argument("--apagar-brutos", action="store_true",
                        help="apaga cada arquivo bruto depois de processado (economiza ~3 GB no backfill)")
    args = parser.parse_args(argv)
    try:
        with requests.Session() as session:
            executar(
                args.modo,
                session=session,
                raw_dir=args.raw_dir,
                processed_dir=args.processed_dir,
                out_dir=args.out_dir,
                schemas_dir=args.schemas_dir,
                agora=datetime.now(timezone.utc),
                apagar_brutos=args.apagar_brutos,
            )
    except Exception as erro:  # noqa: BLE001 — a mensagem vai para o log do Actions
        print(f"ERRO: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest tests/test_cli.py -v`
Esperado: 5 passed.

- [ ] **Passo 5: Rodar a suíte inteira**

Rodar: `cd pipeline && .venv/Scripts/python -m pytest -q`
Esperado: todos passam.

- [ ] **Passo 6: Commit**

```bash
git add pipeline/src/anp/cli.py pipeline/tests/test_cli.py
git commit -m "feat(pipeline): comandos backfill e update" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Carga histórica real (execução local)

Esta tarefa acessa a internet e demora. São cerca de 45 arquivos semestrais, que ocupam uns 3 GB se forem mantidos. Ela não cria código novo: gera os dados reais e confere se estão plausíveis.

**Arquivos:**
- Criar (gerados): `pipeline/data/processed/diario_2004.csv` … `diario_2026.csv`, `pipeline/data/processed/ipca.csv`
- Criar (gerados): `site/public/data/evolucao.json`, `ranking_uf.json`, `etanol_gasolina.json`, `meta.json`

**Interfaces:**
- Produz: os dados reais que a Parte 2 exibe e que o workflow semanal passa a atualizar.

- [ ] **Passo 1: Rodar o backfill**

```bash
cd pipeline
.venv/Scripts/anp backfill
```

Esperado: uma linha `processando ...` por arquivo e, no fim, `OK: <N> linhas na base, última data 2026-09-..`. Se algum download falhar mesmo depois das 5 tentativas, basta rodar o mesmo comando de novo: os arquivos já baixados ficam em cache em `pipeline/data/raw/`. Se a validação falhar, leia a lista de erros. Ela diz qual regra falhou e para qual UF ou semana.

- [ ] **Passo 2: Conferir os números contra valores conhecidos**

```bash
cd pipeline
.venv/Scripts/python - <<'EOF'
import json
from pathlib import Path
d = Path("../site/public/data")
evo = json.loads((d / "evolucao.json").read_text(encoding="utf-8"))
meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
br = evo["series"]["BR"]["gasolina"]
print("primeiro mês:", evo["meses"][0], "gasolina BR nominal:", br["nominal"][0])
print("último mês:", evo["meses"][-1], "gasolina BR nominal:", br["nominal"][-1], "real:", br["real"][-1])
print("diesel S10 BR começa em:", evo["meses"][next(i for i, v in enumerate(evo["series"]["BR"]["diesel_s10"]["nominal"]) if v)])
print("meta:", json.dumps(meta["destaques"], ensure_ascii=False))
print("UFs:", len(evo["series"]) - 1)
EOF
```

Esperado, aproximadamente:
- primeiro mês `2004-05`, gasolina BR entre 1,9 e 2,2;
- último mês entre 5,5 e 7,5;
- diesel S10 começando em `2013-01`;
- `UFs: 27`;
- `gasolina_df` entre 5 e 8.

Se algum número sair muito diferente, **não faça commit**: investigue a limpeza. O primeiro suspeito é o mapeamento de produtos.

- [ ] **Passo 3: Conferir o tamanho da base versionada**

```bash
du -sh pipeline/data/processed site/public/data
```

Esperado: `processed` com algo entre 10 e 25 MB e `data` com menos de 2 MB. Se `processed` passar de 50 MB, pare e reavalie o formato antes de fazer commit.

- [ ] **Passo 4: Commit dos dados**

```bash
git add pipeline/data/processed site/public/data
git commit -m "data: carga histórica ANP 2004–2026" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 12: Workflow semanal no GitHub Actions

**Arquivos:**
- Criar: `.github/workflows/update-data.yml`

**Interfaces:**
- Consome: o comando `anp` (Tarefa 10) e os dados versionados (Tarefa 11).
- Produz: o job `update`, com a saída `changed` igual a `"true"` quando houve commit. A Parte 2 (Tarefa 12 dela) acrescenta um job `deploy` que usa essa saída.

- [ ] **Passo 1: Escrever o workflow**

```yaml
name: Atualizar dados ANP

on:
  schedule:
    - cron: "0 12 * * 6" # sábado, 9h em Brasília
  workflow_dispatch:
    inputs:
      mode:
        description: "update (semanal) ou backfill (refaz toda a série)"
        type: choice
        options: [update, backfill]
        default: update

concurrency:
  group: update-data
  cancel-in-progress: false

jobs:
  update:
    runs-on: ubuntu-latest
    timeout-minutes: 180
    permissions:
      contents: write
    outputs:
      changed: ${{ steps.commit.outputs.changed }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: pipeline/pyproject.toml

      - name: Instalar pipeline
        run: pip install -e "pipeline[dev]"

      - name: Testes
        working-directory: pipeline
        run: pytest -q

      - name: Rodar pipeline (${{ inputs.mode || 'update' }})
        run: anp ${{ inputs.mode || 'update' }} --apagar-brutos

      - name: Commit se os dados mudaram
        id: commit
        run: |
          git add pipeline/data/processed site/public/data
          if git diff --cached --quiet -- pipeline/data/processed; then
            echo "Nenhum dado novo."
            git reset -q
            echo "changed=false" >> "$GITHUB_OUTPUT"
            exit 0
          fi
          semana=$(python -c "import json;print(json.load(open('site/public/data/meta.json'))['semana_mais_recente'])")
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git commit -m "data: atualização semanal ANP (semana ${semana})"
          git push
          echo "changed=true" >> "$GITHUB_OUTPUT"
```

- [ ] **Passo 2: Validar a sintaxe do workflow**

```bash
pipeline/.venv/Scripts/python -m pip install actionlint-py
pipeline/.venv/Scripts/actionlint .github/workflows/update-data.yml
```

Esperado: nenhuma saída, o que significa que não há erros. O `actionlint-py` é só uma ferramenta de verificação local e **não** entra no `pyproject.toml`.

- [ ] **Passo 3: Commit**

```bash
git add .github/workflows/update-data.yml
git commit -m "ci: atualização semanal dos dados ANP" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

O workflow só roda de verdade depois que o repositório for publicado no GitHub (Parte 2, Tarefa 13). Lá ele é disparado manualmente uma vez para confirmar que funciona.
