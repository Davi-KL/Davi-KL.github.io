import { computed, type ComputedRef } from "vue"
import { useI18n } from "vue-i18n"
import en from "../content/en.json"
import pt from "../content/pt.json"

export type Conteudo = typeof pt.conteudo

const POR_IDIOMA: Record<string, Conteudo> = { pt: pt.conteudo, en: en.conteudo }

export function useConteudo(): ComputedRef<Conteudo> {
  const { locale } = useI18n()
  return computed(() => POR_IDIOMA[locale.value] ?? pt.conteudo)
}
