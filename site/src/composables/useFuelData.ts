import { ref, type Ref } from "vue"

export type ArquivoDados = "meta.json" | "evolucao.json" | "ranking_uf.json" | "etanol_gasolina.json"

const cache = new Map<string, Promise<unknown>>()

export function limparCacheDados(): void {
  cache.clear()
}

export function carregarJson<T>(arquivo: ArquivoDados): Promise<T> {
  const url = `${import.meta.env.BASE_URL}data/${arquivo}`
  let promessa = cache.get(url)
  if (!promessa) {
    promessa = fetch(url).then((resposta) => {
      if (!resposta.ok) throw new Error(`HTTP ${resposta.status} ao carregar ${arquivo}`)
      return resposta.json()
    })
    promessa.catch(() => cache.delete(url))
    cache.set(url, promessa)
  }
  return promessa as Promise<T>
}

export interface EstadoDados<T> {
  dados: Ref<T | null>
  erro: Ref<boolean>
  carregando: Ref<boolean>
}

export function useFuelData<T>(arquivo: ArquivoDados): EstadoDados<T> {
  const dados = ref(null) as Ref<T | null>
  const erro = ref(false)
  const carregando = ref(true)
  carregarJson<T>(arquivo)
    .then((valor) => {
      dados.value = valor
    })
    .catch(() => {
      erro.value = true
    })
    .finally(() => {
      carregando.value = false
    })
  return { dados, erro, carregando }
}
