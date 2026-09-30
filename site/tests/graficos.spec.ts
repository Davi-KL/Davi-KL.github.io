import { describe, expect, it } from "vitest"
import etanol from "../src/__fixtures__/etanol_gasolina.json"
import evolucao from "../src/__fixtures__/evolucao.json"
import ranking from "../src/__fixtures__/ranking_uf.json"
import { COR_DESTAQUE, CORES_PRODUTO, mesclarLayout } from "../src/lib/chartTheme"
import {
  tabelaEvolucao,
  tabelaRanking,
  tabelaRazao,
  tracosEvolucao,
  tracosRanking,
  tracosRazaoAtual,
  tracosRazaoHistorico,
} from "../src/lib/graficos"
import { insightEvolucao, insightRanking, ufsEtanol } from "../src/lib/insights"
import type { EtanolGasolina, Evolucao, Ranking } from "../src/types/dados"

const evo = evolucao as Evolucao
const rk = ranking as Ranking
const eg = etanol as EtanolGasolina

describe("evolução", () => {
  it("linha do Brasil na cor do produto e da UF em destaque", () => {
    const [br, df] = tracosEvolucao(evo, "gasolina", "DF", "real", { brasil: "Brasil", uf: "DF" })
    expect(br.y).toEqual([6.43, 6.48, 6.52, 6.558])
    expect((br.line as { color: string }).color).toBe(CORES_PRODUTO.gasolina)
    expect(df.name).toBe("DF")
    expect((df.line as { color: string }).color).toBe(COR_DESTAQUE)
  })

  it("com a UF igual a BR, uma linha só", () => {
    expect(tracosEvolucao(evo, "etanol", "BR", "nominal", { brasil: "Brasil", uf: "BR" })).toHaveLength(1)
  })

  it("UF sem série vira nulos em vez de quebrar", () => {
    const [, xx] = tracosEvolucao(evo, "gasolina", "XX", "real", { brasil: "Brasil", uf: "XX" })
    expect(xx.y).toEqual([null, null, null, null])
  })

  it("tabela do mês mais recente para o mais antigo, com traço nos buracos", () => {
    const tab = tabelaEvolucao(evo, "diesel_s10", "DF", "nominal", { mes: "Mês", brasil: "Brasil", uf: "DF" }, (m) => m, (v) => (v === null ? "—" : v.toFixed(2)))
    expect(tab.colunas).toEqual(["Mês", "Brasil", "DF"])
    expect(tab.linhas[0]).toEqual(["2026-09", "6.90", "6.95"])
    expect(tab.linhas[3]).toEqual(["2026-06", "6.80", "—"])
  })
})

describe("ranking", () => {
  const fmtVar = (v: number | null) => (v === null ? "—" : `${v}%`)

  it("barras do menor para o maior (maior no topo), DF em destaque, média BR como referência", () => {
    const { tracos, referencia } = tracosRanking(rk, "gasolina", fmtVar)
    expect(tracos[0].y).toEqual(["SP", "DF", "AC"])
    expect((tracos[0].marker as { color: string[] }).color).toEqual([CORES_PRODUTO.gasolina, COR_DESTAQUE, CORES_PRODUTO.gasolina])
    expect(tracos[0].customdata).toEqual(["2%", "2.9%", "5%"])
    expect(referencia).toBe(6.558)
  })

  it("tabela do mais caro para o mais barato", () => {
    const tab = tabelaRanking(rk, "etanol", { estado: "UF", preco: "Preço", variacao: "12m", coletas: "n" }, (v) => v.toFixed(2), fmtVar)
    expect(tab.linhas.map((l) => l[0])).toEqual(["AC", "DF", "SP"])
    expect(tab.linhas[1]).toEqual(["DF", "4.38", "—", "1100"])
  })
})

describe("etanol × gasolina", () => {
  it("separa quem compensa etanol e ordena com a menor razão no topo", () => {
    const { tracos, ordem } = tracosRazaoAtual(eg, { etanol: "Etanol", gasolina: "Gasolina" })
    expect(tracos[0].y).toEqual(["SP", "DF"])
    expect(tracos[1].y).toEqual(["AC"])
    // categoryarray do Plotly: o primeiro item fica embaixo, então a menor razão (SP) vai para o topo
    expect(ordem).toEqual(["AC", "DF", "SP"])
  })

  it("histórico com Brasil e a UF", () => {
    const [br, df] = tracosRazaoHistorico(eg, "DF", { brasil: "Brasil", uf: "DF" })
    expect(br.y).toEqual([0.655, 0.657, 0.656, 0.656])
    expect(df.y).toEqual([0.662, 0.661, null, 0.657])
  })

  it("tabela da menor para a maior razão", () => {
    const tab = tabelaRazao(eg, { estado: "UF", razao: "Razão", compensa: "Compensa" }, (v) => v.toFixed(3), { etanol: "Etanol", gasolina: "Gasolina" })
    expect(tab.linhas).toEqual([["SP", "0.594", "Etanol"], ["DF", "0.657", "Etanol"], ["AC", "0.725", "Gasolina"]])
  })
})

describe("insights", () => {
  it("evolução real da gasolina no Brasil", () => {
    const i = insightEvolucao(evo)
    expect(i?.mesInicial).toBe("2026-06")
    expect(i?.inicial).toBe(6.43)
    expect(i?.atual).toBe(6.558)
    expect(i?.variacaoPct).toBeCloseTo(1.99, 1)
  })

  it("ranking: mais cara, mais barata e posição do DF", () => {
    const i = insightRanking(rk, "gasolina")
    expect(i?.maisCara.uf).toBe("AC")
    expect(i?.maisBarata.uf).toBe("SP")
    expect(i?.posicao).toBe(2)
    expect(i?.total).toBe(3)
  })

  it("estados onde o etanol compensa, da menor razão para a maior", () => {
    expect(ufsEtanol(eg)).toEqual(["SP", "DF"])
  })
})

describe("layout", () => {
  it("mescla eixos sem perder o tema", () => {
    const l = mesclarLayout({ yaxis: { tickprefix: "R$ " } }, 400)
    expect(l.height).toBe(400)
    expect((l.yaxis as Record<string, unknown>).tickprefix).toBe("R$ ")
    expect((l.yaxis as Record<string, unknown>).gridcolor).toBe("#1e293b")
  })
})
