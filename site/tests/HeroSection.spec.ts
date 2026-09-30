import { afterEach, describe, expect, it } from "vitest"
import meta from "../src/__fixtures__/meta.json"
import HeroSection from "../src/components/home/HeroSection.vue"
import { cv } from "../src/content/perfil"
import { montar, simularDados, texto } from "./montar"

describe("HeroSection", () => {
  afterEach(() => {
    cv.pt = null
    cv.en = null
  })

  it("mostra frase, números e o preço da gasolina no DF", async () => {
    simularDados({ "meta.json": meta })
    const w = await montar(HeroSection)
    expect(w.get("h1").text()).toBe("Código que resolve. Dados que explicam.")
    expect(w.findAll(".numero__valor").map((e) => texto(e))).toEqual(["2+", "6", "R$ 6,67"])
    expect(texto(w)).toContain("projetos em destaque")
    expect(texto(w.get("[data-testid='gasolina-df']"))).toContain("gasolina no DF hoje")
  })

  it("sem dados, esconde só o número da gasolina", async () => {
    simularDados({})
    const w = await montar(HeroSection)
    expect(w.find("[data-testid='gasolina-df']").exists()).toBe(false)
    expect(w.findAll(".numero__valor").map((e) => e.text())).toEqual(["2+", "6"])
  })

  it("botão de CV só aparece quando o arquivo existe", async () => {
    simularDados({})
    expect((await montar(HeroSection)).text()).not.toContain("Baixar CV")
    cv.pt = "/cv/cv-pt.pdf"
    const w = await montar(HeroSection)
    expect(w.get("a[download]").attributes("href")).toBe("/cv/cv-pt.pdf")
  })

  it("em inglês", async () => {
    simularDados({ "meta.json": meta })
    const w = await montar(HeroSection, { idioma: "en" })
    expect(w.get("h1").text()).toBe("Code that solves. Data that explains.")
    expect(w.get("[data-testid='gasolina-df']").text()).toContain("R$6.67")
  })
})
