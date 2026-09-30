import { flushPromises, mount, type VueWrapper } from "@vue/test-utils"
import { vi } from "vitest"
import type { Component } from "vue"
import { createMemoryHistory } from "vue-router"
import { limparCacheDados } from "../src/composables/useFuelData"
import { i18n, type Idioma } from "../src/i18n"
import { criarRouter } from "../src/router"

/** Simula o fetch dos JSONs. Número = status HTTP de erro; "rede" = falha de rede; chave ausente = 404. */
export function simularDados(respostas: Record<string, unknown>) {
  limparCacheDados()
  const fetch = vi.fn(async (url: string | URL) => {
    const nome = String(url).split("/").pop() ?? ""
    const resposta = respostas[nome]
    if (resposta === "rede") throw new TypeError("Failed to fetch")
    const status = resposta === undefined ? 404 : typeof resposta === "number" ? resposta : 200
    return { ok: status === 200, status, json: async () => resposta } as Response
  })
  vi.stubGlobal("fetch", fetch)
  return fetch
}

export async function montar(
  componente: Component,
  opcoes: { props?: Record<string, unknown>; slots?: Record<string, () => unknown>; rota?: string; idioma?: Idioma } = {},
): Promise<VueWrapper> {
  i18n.global.locale.value = opcoes.idioma ?? "pt"
  const router = criarRouter(createMemoryHistory())
  await router.push(opcoes.rota ?? "/")
  await router.isReady()
  const wrapper = mount(componente, {
    props: opcoes.props,
    slots: opcoes.slots as never,
    global: { plugins: [i18n, router] },
  })
  await flushPromises()
  await flushPromises()
  return wrapper
}

/** Texto do componente (ou de um elemento dele) com espaços normalizados, inclusive o espaço fixo do "R$ ". */
export const texto = (w: { text(): string }): string => w.text().replace(/\s+/g, " ")
