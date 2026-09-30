import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import etanol from "../src/__fixtures__/etanol_gasolina.json"
import evolucao from "../src/__fixtures__/evolucao.json"
import meta from "../src/__fixtures__/meta.json"
import ranking from "../src/__fixtures__/ranking_uf.json"
import FuelDataView from "../src/views/FuelDataView.vue"
import { montar, simularDados, texto } from "./montar"

const plotly = vi.hoisted(() => ({ react: vi.fn(async () => undefined), purge: vi.fn() }))
vi.mock("plotly.js-basic-dist-min", () => ({ default: plotly }))

const TODOS = { "meta.json": meta, "evolucao.json": evolucao, "ranking_uf.json": ranking, "etanol_gasolina.json": etanol }

describe("FuelDataView", () => {
  beforeEach(() => vi.useFakeTimers({ now: new Date("2026-09-30T12:00:00Z"), toFake: ["Date"] }))
  afterEach(() => vi.useRealTimers())

  it("mostra título, data dos dados e as três análises com insights", async () => {
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    const t = texto(w)
    expect(w.get("h1").text()).toBe("Quanto custa abastecer no Brasil?")
    expect(t).toContain("Dados até a semana de 21/09/2026.")
    expect(w.find("[data-testid='aviso-desatualizado']").exists()).toBe(false)
    expect(t).toContain("custava R$ 6,43 em 06/2026 e custa R$ 6,56 hoje: +2,0%")
    expect(t).toContain("Preço mais alto: AC (R$ 7,45)")
    expect(t).toContain("O DF é o 2º mais caro entre 3 estados")
    expect(t).toContain("O etanol compensa em 2 estados: SP, DF.")
    expect(t).toContain("Metodologia")
    expect(document.title).toBe("Preços dos combustíveis no Brasil — Davi Levy")
    await vi.waitFor(() => expect(plotly.react).toHaveBeenCalled())
  })

  it("avisa quando os dados têm mais de 21 dias", async () => {
    vi.setSystemTime(new Date("2026-11-01T12:00:00Z"))
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    expect(w.get("[data-testid='aviso-desatualizado']").text()).toContain("dados de 21/09")
  })

  it("um arquivo com erro não derruba as outras análises", async () => {
    simularDados({ ...TODOS, "evolucao.json": 500 })
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    expect(texto(w.get("[data-testid='analise-evolucao']"))).toContain("Dados indisponíveis no momento.")
    expect(texto(w.get("[data-testid='analise-ranking']"))).toContain("Preço mais alto")
  })

  it("trocar o combustível no ranking atualiza o insight", async () => {
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    await w.get("[data-testid='ranking-produto']").setValue("etanol")
    expect(texto(w.get("[data-testid='analise-ranking']"))).toContain("Preço mais alto: AC (R$ 5,40)")
  })

  it("em inglês", async () => {
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis", idioma: "en" })
    expect(w.get("h1").text()).toBe("How much does it cost to fill up in Brazil?")
    expect(texto(w)).toContain("Data up to the week of Sep 21, 2026.")
  })
})
