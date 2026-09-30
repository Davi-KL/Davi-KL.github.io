import { afterEach, describe, expect, it } from "vitest"
import meta from "../src/__fixtures__/meta.json"
import ContactSection from "../src/components/home/ContactSection.vue"
import FuelPreviewSection from "../src/components/home/FuelPreviewSection.vue"
import { cv } from "../src/content/perfil"
import { montar, simularDados, texto } from "./montar"

describe("Prévia da análise", () => {
  it("mostra três insights, minigráfico e link para a análise", async () => {
    simularDados({ "meta.json": meta })
    const w = await montar(FuelPreviewSection)
    expect(w.findAll("li")).toHaveLength(3)
    expect(texto(w)).toContain("+1,7% em relação à média nacional")
    expect(texto(w)).toContain("O etanol compensa em 11 dos 27 estados")
    expect(texto(w)).toContain("diesel S10 em AC (+8,1%)")
    expect(w.findAll("svg path")).toHaveLength(2)
    expect(w.find("a[href='/dados-combustiveis']").exists()).toBe(true)
  })

  it("some por completo se os dados falharem", async () => {
    simularDados({ "meta.json": 500 })
    const w = await montar(FuelPreviewSection)
    expect(w.find("[data-testid='previa-anp']").exists()).toBe(false)
  })

  it("sem maior alta, mostra só dois insights", async () => {
    simularDados({ "meta.json": { ...meta, destaques: { ...meta.destaques, maior_alta_12m: null } } })
    const w = await montar(FuelPreviewSection)
    expect(w.findAll("li")).toHaveLength(2)
  })
})

describe("Contato", () => {
  afterEach(() => {
    cv.pt = null
  })

  it("tem e-mail, LinkedIn e GitHub; CV só com arquivo", async () => {
    const w = await montar(ContactSection)
    expect(w.attributes("id")).toBe("contato")
    expect(w.get("[data-testid='contato-email']").attributes("href")).toBe("mailto:daviklevy@gmail.com")
    expect(w.find("a[href='https://www.linkedin.com/in/davi-levy-dev']").exists()).toBe(true)
    expect(w.find("a[href='https://github.com/Davi-KL']").exists()).toBe(true)
    expect(w.find("[data-testid='contato-cv']").exists()).toBe(false)
    cv.pt = "/cv/cv-pt.pdf"
    const comCv = await montar(ContactSection)
    expect(comCv.get("[data-testid='contato-cv']").attributes("href")).toBe("/cv/cv-pt.pdf")
  })
})
