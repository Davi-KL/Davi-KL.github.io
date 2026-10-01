import { afterEach, describe, expect, it } from "vitest"
import HeroSection from "../src/components/home/HeroSection.vue"
import { cv } from "../src/content/perfil"
import { montar, texto } from "./montar"

describe("HeroSection", () => {
  afterEach(() => {
    cv.pt = null
    cv.en = null
  })

  it("mostra frase e números de destaque, sem card de dados soltos", async () => {
    const w = await montar(HeroSection)
    expect(w.get("h1").text()).toBe("Código que resolve. Dados que explicam.")
    expect(w.findAll(".numero__valor").map((e) => texto(e))).toEqual(["2+", "6"])
    expect(texto(w)).toContain("projetos em destaque")
    expect(w.find("[data-testid='gasolina-df']").exists()).toBe(false)
  })

  it("botão de CV só aparece quando o arquivo existe", async () => {
    expect((await montar(HeroSection)).text()).not.toContain("Baixar CV")
    cv.pt = "/cv/cv-pt.pdf"
    const w = await montar(HeroSection)
    expect(w.get("a[download]").attributes("href")).toBe("/cv/cv-pt.pdf")
  })

  it("em inglês", async () => {
    const w = await montar(HeroSection, { idioma: "en" })
    expect(w.get("h1").text()).toBe("Code that solves. Data that explains.")
  })

  it("mostra a foto de perfil com o alt certo em cada idioma", async () => {
    const pt = await montar(HeroSection)
    const foto = pt.get("[data-testid='hero-foto']")
    expect(foto.attributes("src")).toBe("/foto-davi.jpg")
    expect(foto.attributes("alt")).toBe("Foto de Davi Levy")

    const en = await montar(HeroSection, { idioma: "en" })
    expect(en.get("[data-testid='hero-foto']").attributes("alt")).toBe("Photo of Davi Levy")
  })
})
