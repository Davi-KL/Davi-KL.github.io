import { afterEach, describe, expect, it } from "vitest"
import SiteHeader from "../src/components/layout/SiteHeader.vue"
import { i18n } from "../src/i18n"
import { montar, texto } from "./montar"

describe("SiteHeader", () => {
  afterEach(() => localStorage.clear())

  it("mostra a navegação em português", async () => {
    const w = await montar(SiteHeader)
    expect(texto(w)).toContain("Sobre")
    expect(texto(w)).toContain("Projetos")
    expect(w.find("nav a[href='/dados-combustiveis']").exists()).toBe(true)
  })

  it("troca para inglês, ajusta o lang e salva a escolha", async () => {
    const w = await montar(SiteHeader)
    await w.get("[data-testid='trocar-idioma']").trigger("click")
    expect(i18n.global.locale.value).toBe("en")
    expect(texto(w)).toContain("About")
    expect(document.documentElement.lang).toBe("en")
    expect(localStorage.getItem("idioma")).toBe("en")
  })

  it("menu móvel abre e fecha", async () => {
    const w = await montar(SiteHeader)
    const botao = w.get("[data-testid='menu']")
    expect(botao.attributes("aria-expanded")).toBe("false")
    await botao.trigger("click")
    expect(botao.attributes("aria-expanded")).toBe("true")
  })
})
