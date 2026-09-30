import { createI18n } from "vue-i18n"
import en from "./content/en.json"
import pt from "./content/pt.json"

export type Idioma = "pt" | "en"

const CHAVE = "idioma"

function lerLinguas(): readonly string[] {
  if (typeof navigator === "undefined") return []
  return navigator.languages?.length ? navigator.languages : [navigator.language]
}

function lerSalvo(): string | null {
  try {
    return localStorage.getItem(CHAVE)
  } catch {
    return null
  }
}

export function idiomaInicial(linguas: readonly string[] = lerLinguas(), salvo: string | null = lerSalvo()): Idioma {
  if (salvo === "pt" || salvo === "en") return salvo
  const primeira = linguas[0]?.toLowerCase()
  return !primeira || primeira.startsWith("pt") ? "pt" : "en"
}

export const i18n = createI18n({
  legacy: false,
  locale: idiomaInicial(),
  fallbackLocale: "pt",
  messages: { pt: pt.ui, en: en.ui },
})

export function aplicarLang(idioma: Idioma): void {
  document.documentElement.lang = idioma === "pt" ? "pt-BR" : "en"
}

export function definirIdioma(idioma: Idioma): void {
  i18n.global.locale.value = idioma
  aplicarLang(idioma)
  try {
    localStorage.setItem(CHAVE, idioma)
  } catch {
    // navegação privada: segue sem salvar
  }
}
