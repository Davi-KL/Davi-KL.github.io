import { describe, expect, it } from "vitest"
import {
  formatarData,
  formatarDiaMes,
  formatarMes,
  formatarNumero,
  formatarPct,
  formatarRazao,
  formatarReais,
} from "../src/lib/format"

const normal = (s: string) => s.replace(/\s/g, " ")

describe("formatação", () => {
  it("reais", () => {
    expect(normal(formatarReais(6.669, "pt"))).toBe("R$ 6,67")
    expect(formatarReais(6.669, "en")).toBe("R$6.67")
  })
  it("percentual com sinal, em pontos percentuais", () => {
    expect(formatarPct(1.7, "pt")).toBe("+1,7%")
    expect(formatarPct(-2.5, "en")).toBe("-2.5%")
    expect(formatarPct(0, "pt")).toBe("0,0%")
  })
  it("razão", () => {
    expect(formatarRazao(0.657, "pt")).toBe("65,7%")
    expect(formatarRazao(0.657, "en")).toBe("65.7%")
  })
  it("datas sem deslocamento de fuso", () => {
    expect(formatarData("2026-09-21", "pt")).toBe("21/09/2026")
    expect(formatarData("2026-09-21", "en")).toBe("Sep 21, 2026")
    expect(formatarDiaMes("2026-09-21", "pt")).toBe("21/09")
    expect(formatarDiaMes("2026-09-21", "en")).toBe("Sep 21")
    expect(formatarMes("2026-08", "pt")).toBe("08/2026")
  })
  it("números inteiros", () => {
    expect(formatarNumero(420419, "pt")).toBe("420.419")
    expect(formatarNumero(420419, "en")).toBe("420,419")
  })
})
