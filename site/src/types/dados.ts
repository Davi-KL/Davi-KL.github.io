export type Produto = "gasolina" | "etanol" | "diesel_s10"
export type Serie = (number | null)[]

export interface SerieProduto {
  nominal: Serie
  real: Serie
}

export interface Evolucao {
  meses: string[]
  ipca_ref: string
  series: Record<string, Partial<Record<Produto, SerieProduto>>>
}

export interface ItemRanking {
  uf: string
  produto: Produto
  preco_medio: number
  variacao_12m_pct: number | null
  n_coletas: number
}

export interface Ranking {
  periodo: { inicio: string; fim: string }
  itens: ItemRanking[]
}

export interface ItemRazao {
  uf: string
  razao: number
  compensa: "etanol" | "gasolina"
}

export interface EtanolGasolina {
  limiar: number
  atual: ItemRazao[]
  historico: { meses: string[]; razao: Record<string, Serie> }
}

export interface Meta {
  atualizado_em: string
  semana_mais_recente: string
  n_coletas_total: number
  ipca_ate: string
  ipca_em_cache: boolean
  fontes: { nome: string; url: string }[]
  destaques: {
    gasolina_df: number
    gasolina_br: number
    diff_df_br_pct: number | null
    ufs_etanol_compensa: number
    maior_alta_12m: { uf: string; produto: Produto; pct: number } | null
  }
  serie_home: { meses: string[]; gasolina_br: Serie; gasolina_df: Serie }
}
