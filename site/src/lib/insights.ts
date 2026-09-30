import type { EtanolGasolina, Evolucao, ItemRanking, Produto, Ranking } from "../types/dados"
import { itensRanking, itensRazao, serieEvolucao } from "./graficos"

export function insightEvolucao(
  evo: Evolucao, produto: Produto = "gasolina",
): { mesInicial: string; inicial: number; atual: number; variacaoPct: number } | null {
  const serie = serieEvolucao(evo, "BR", produto, "real")
  const primeiro = serie.findIndex((v) => v !== null)
  let ultimo = -1
  for (let i = serie.length - 1; i >= 0; i--) {
    if (serie[i] !== null) {
      ultimo = i
      break
    }
  }
  if (primeiro < 0 || ultimo <= primeiro) return null
  const inicial = serie[primeiro] as number
  const atual = serie[ultimo] as number
  return { mesInicial: evo.meses[primeiro], inicial, atual, variacaoPct: (atual / inicial - 1) * 100 }
}

export function insightRanking(
  r: Ranking, produto: Produto, uf = "DF",
): { maisCara: ItemRanking; maisBarata: ItemRanking; posicao: number; total: number } | null {
  const itens = itensRanking(r, produto)
  if (!itens.length) return null
  return {
    maisCara: itens[0],
    maisBarata: itens[itens.length - 1],
    posicao: itens.findIndex((i) => i.uf === uf) + 1,
    total: itens.length,
  }
}

export function ufsEtanol(eg: EtanolGasolina): string[] {
  return itensRazao(eg).filter((i) => i.compensa === "etanol").map((i) => i.uf)
}
