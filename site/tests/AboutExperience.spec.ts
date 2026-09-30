import { describe, expect, it } from "vitest"
import AboutSection from "../src/components/home/AboutSection.vue"
import ExperienceSection from "../src/components/home/ExperienceSection.vue"
import { montar, texto } from "./montar"

describe("Sobre", () => {
  it("mostra stack agrupada, formação e certificações", async () => {
    const w = await montar(AboutSection)
    expect(w.attributes("id")).toBe("sobre")
    for (const t of ["Front-end", "Back-end", "Dados/IA", "DevOps", "PL/SQL (Oracle)", "Ciência da Computação", "Google AI Essentials"]) {
      expect(texto(w)).toContain(t)
    }
  })
})

describe("Experiência", () => {
  it("destaca a Rede SARAH com os cinco itens e lista as outras", async () => {
    const w = await montar(ExperienceSection)
    expect(w.attributes("id")).toBe("experiencia")
    expect(w.findAll("[data-testid='sarah'] li")).toHaveLength(5)
    expect(texto(w)).toContain("Zenit Aerospace")
    expect(texto(w)).toContain("Sabin Medicina Diagnóstica")
  })
})
