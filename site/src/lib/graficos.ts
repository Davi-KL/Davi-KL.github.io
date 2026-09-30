import type { EtanolGasolina, Evolucao, ItemRanking, ItemRazao, Produto, Ranking, Serie } from "../types/dados"
import { COR_DESTAQUE, COR_REFERENCIA, CORES_PRODUTO } from "./chartTheme"

export type Traco = Record<string, unknown>
export type Modo = "nominal" | "real"
export interface Tabela {
  colunas: string[]
  linhas: string[][]
}
type FmtNulo = (valor: number | null) => string

export function serieEvolucao(evo: Evolucao, regiao: string, produto: Produto, modo: Modo): Serie {
  return evo.series[regiao]?.[produto]?.[modo] ?? evo.meses.map(() => null)
}

function linha(x: string[], y: Serie, nome: string, cor: string, largura: number, hover: string): Traco {
  return { type: "scatter", mode: "lines", name: nome, x, y, line: { color: cor, width: largura }, connectgaps: false, hovertemplate: hover }
}

export function tracosEvolucao(evo: Evolucao, produto: Produto, uf: string, modo: Modo, nomes: { brasil: string; uf: string }): Traco[] {
  const hover = "%{x|%m/%Y}: R$ %{y:.2f}<extra>%{fullData.name}</extra>"
  const tracos = [linha(evo.meses, serieEvolucao(evo, "BR", produto, modo), nomes.brasil, CORES_PRODUTO[produto], 2.5, hover)]
  if (uf !== "BR") tracos.push(linha(evo.meses, serieEvolucao(evo, uf, produto, modo), nomes.uf, COR_DESTAQUE, 2, hover))
  return tracos
}

export function tabelaEvolucao(
  evo: Evolucao, produto: Produto, uf: string, modo: Modo,
  cab: { mes: string; brasil: string; uf: string }, fmtMes: (mes: string) => string, fmtValor: FmtNulo,
): Tabela {
  const br = serieEvolucao(evo, "BR", produto, modo)
  const local = serieEvolucao(evo, uf, produto, modo)
  const linhas = evo.meses.map((m, i) => [fmtMes(m), fmtValor(br[i]), fmtValor(local[i])]).reverse()
  return { colunas: [cab.mes, cab.brasil, cab.uf], linhas }
}

export function itensRanking(r: Ranking, produto: Produto): ItemRanking[] {
  return r.itens.filter((i) => i.produto === produto && i.uf !== "BR").sort((a, b) => b.preco_medio - a.preco_medio)
}

export function tracosRanking(r: Ranking, produto: Produto, fmtVar: FmtNulo, destaque = "DF"): { tracos: Traco[]; altura: number; referencia: number | null } {
  const itens = [...itensRanking(r, produto)].reverse()
  return {
    tracos: [{
      type: "bar",
      orientation: "h",
      x: itens.map((i) => i.preco_medio),
      y: itens.map((i) => i.uf),
      marker: { color: itens.map((i) => (i.uf === destaque ? COR_DESTAQUE : CORES_PRODUTO[produto])) },
      customdata: itens.map((i) => fmtVar(i.variacao_12m_pct)),
      hovertemplate: "%{y}: R$ %{x:.2f} · 12m: %{customdata}<extra></extra>",
    }],
    altura: Math.max(360, itens.length * 22 + 80),
    referencia: r.itens.find((i) => i.uf === "BR" && i.produto === produto)?.preco_medio ?? null,
  }
}

export function tabelaRanking(
  r: Ranking, produto: Produto, cab: { estado: string; preco: string; variacao: string; coletas: string },
  fmtPreco: (valor: number) => string, fmtVar: FmtNulo,
): Tabela {
  return {
    colunas: [cab.estado, cab.preco, cab.variacao, cab.coletas],
    linhas: itensRanking(r, produto).map((i) => [i.uf, fmtPreco(i.preco_medio), fmtVar(i.variacao_12m_pct), String(i.n_coletas)]),
  }
}

export function itensRazao(eg: EtanolGasolina): ItemRazao[] {
  return eg.atual.filter((i) => i.uf !== "BR").sort((a, b) => a.razao - b.razao)
}

export function tracosRazaoAtual(eg: EtanolGasolina, nomes: { etanol: string; gasolina: string }): { tracos: Traco[]; altura: number; ordem: string[] } {
  const itens = itensRazao(eg)
  const grupo = (compensa: "etanol" | "gasolina"): Traco => {
    const selecionados = itens.filter((i) => i.compensa === compensa)
    return {
      type: "bar",
      orientation: "h",
      name: nomes[compensa],
      x: selecionados.map((i) => i.razao),
      y: selecionados.map((i) => i.uf),
      marker: { color: CORES_PRODUTO[compensa] },
      hovertemplate: "%{y}: %{x:.1%}<extra>%{fullData.name}</extra>",
    }
  }
  return {
    tracos: [grupo("etanol"), grupo("gasolina")],
    altura: Math.max(360, itens.length * 22 + 100),
    ordem: itens.map((i) => i.uf).reverse(),
  }
}

export function tracosRazaoHistorico(eg: EtanolGasolina, uf: string, nomes: { brasil: string; uf: string }): Traco[] {
  const serie = (regiao: string): Serie => eg.historico.razao[regiao] ?? eg.historico.meses.map(() => null)
  const hover = "%{x|%m/%Y}: %{y:.1%}<extra>%{fullData.name}</extra>"
  const tracos = [linha(eg.historico.meses, serie("BR"), nomes.brasil, CORES_PRODUTO.etanol, 2.5, hover)]
  if (uf !== "BR") tracos.push(linha(eg.historico.meses, serie(uf), nomes.uf, COR_DESTAQUE, 2, hover))
  return tracos
}

export function tabelaRazao(
  eg: EtanolGasolina, cab: { estado: string; razao: string; compensa: string },
  fmtRazao: (valor: number) => string, rotulos: { etanol: string; gasolina: string },
): Tabela {
  return {
    colunas: [cab.estado, cab.razao, cab.compensa],
    linhas: itensRazao(eg).map((i) => [i.uf, fmtRazao(i.razao), rotulos[i.compensa]]),
  }
}

export function linhaVertical(x: number): Record<string, unknown> {
  return { type: "line", xref: "x", yref: "paper", x0: x, x1: x, y0: 0, y1: 1, line: { color: COR_REFERENCIA, width: 1.5, dash: "dash" } }
}

export function linhaHorizontal(y: number): Record<string, unknown> {
  return { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: y, y1: y, line: { color: COR_REFERENCIA, width: 1.5, dash: "dash" } }
}
