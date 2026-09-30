import { describe, expect, it } from "vitest"
import { dadosDesatualizados, diasDesde } from "../src/lib/stale"

describe("dados desatualizados", () => {
  const agora = new Date("2026-09-30T12:00:00Z")
  it("conta dias desde a data", () => {
    expect(diasDesde("2026-09-21", agora)).toBe(9)
  })
  it("até 21 dias está em dia", () => {
    expect(dadosDesatualizados("2026-09-09", agora)).toBe(false)
  })
  it("mais de 21 dias está desatualizado", () => {
    expect(dadosDesatualizados("2026-09-08", agora)).toBe(true)
  })
})
