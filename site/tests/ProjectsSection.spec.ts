import { describe, expect, it } from "vitest"
import ProjectsSection from "../src/components/home/ProjectsSection.vue"
import { montar, texto } from "./montar"

describe("ProjectsSection", () => {
  it("mostra os seis projetos na ordem, cada um com o papel", async () => {
    const w = await montar(ProjectsSection)
    const cards = w.findAll("article")
    expect(cards.map((c) => c.attributes("data-testid"))).toEqual([
      "projeto-nodus", "projeto-forunb", "projeto-soma", "projeto-anp", "projeto-flowpad", "projeto-compiladores",
    ])
    for (const card of cards) expect(card.text()).toContain("Meu papel")
  })

  it("NODUS descreve o app desktop offline e o papel de gerente/Scrum Master", async () => {
    const w = await montar(ProjectsSection)
    const nodus = texto(w.get("[data-testid='projeto-nodus']"))
    expect(nodus).toContain("Electron")
    expect(nodus).toContain("Scrum Master")
    expect(w.get("[data-testid='projeto-nodus'] a[href*='cathsatile/NODUS']").attributes("target")).toBe("_blank")
  })

  it("o card da ANP tem link interno para a análise", async () => {
    const w = await montar(ProjectsSection)
    expect(w.find("[data-testid='projeto-anp'] a[href='/dados-combustiveis']").exists()).toBe(true)
  })

  it("tem link para todos os repositórios", async () => {
    const w = await montar(ProjectsSection)
    expect(w.find("a[href='https://github.com/Davi-KL?tab=repositories']").exists()).toBe(true)
  })

  it("em inglês", async () => {
    const w = await montar(ProjectsSection, { idioma: "en" })
    expect(texto(w)).toContain("My role")
    expect(texto(w)).toContain("Portugol Lexical Analyzer")
  })
})
