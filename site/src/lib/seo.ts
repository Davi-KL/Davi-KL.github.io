import type { Idioma } from "../i18n"

function definirMeta(atributo: "name" | "property", chave: string, valor: string): void {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${atributo}="${chave}"]`)
  if (!el) {
    el = document.createElement("meta")
    el.setAttribute(atributo, chave)
    document.head.appendChild(el)
  }
  el.setAttribute("content", valor)
}

export function aplicarMeta({ titulo, descricao, idioma }: { titulo: string; descricao: string; idioma: Idioma }): void {
  document.title = titulo
  definirMeta("name", "description", descricao)
  definirMeta("property", "og:title", titulo)
  definirMeta("property", "og:description", descricao)
  definirMeta("property", "og:locale", idioma === "pt" ? "pt_BR" : "en_US")
}
