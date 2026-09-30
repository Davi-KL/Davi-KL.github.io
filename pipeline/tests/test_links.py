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
