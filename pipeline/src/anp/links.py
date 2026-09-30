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
