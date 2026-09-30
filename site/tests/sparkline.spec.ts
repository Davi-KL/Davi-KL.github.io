import { describe, expect, it } from "vitest"
import { caminhoSparkline, dominio } from "../src/lib/sparkline"

describe("sparkline", () => {
  it("domínio conjunto ignora nulos", () => {
    expect(dominio([[1, null, 3], [2, 5]])).toEqual([1, 5])
    expect(dominio([[null]])).toBeNull()
  })

  it("desenha pontos na escala", () => {
    expect(caminhoSparkline([1, 2, 3], 104, 24, [1, 3])).toBe("M4.0,20.0 L52.0,12.0 L100.0,4.0")
  })

  it("interrompe a linha em buracos", () => {
    expect(caminhoSparkline([1, null, 3], 104, 24, [1, 3])).toBe("M4.0,20.0 M100.0,4.0")
  })

  it("série constante fica na base", () => {
    expect(caminhoSparkline([2, 2], 104, 24, [2, 2])).toBe("M4.0,20.0 L100.0,20.0")
  })

  it("menos de dois pontos não desenha", () => {
    expect(caminhoSparkline([2], 104, 24, [2, 2])).toBe("")
  })
})
