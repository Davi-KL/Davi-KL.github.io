import Ajv2020 from "ajv/dist/2020"
import { existsSync, readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

// Caminhos pelo Node (e não `new URL(..., import.meta.url)`, que o Vite trata como asset e bloqueia fora de site/).
const SITE = join(dirname(fileURLToPath(import.meta.url)), "..")
const ARQUIVOS = ["meta", "evolucao", "ranking_uf", "etanol_gasolina"] as const
const ler = (caminho: string) => JSON.parse(readFileSync(caminho, "utf8"))
const schema = (nome: string) => ler(join(SITE, "..", "schemas", `${nome}.schema.json`))

function validar(nome: string, dados: unknown): string | null {
  const ajv = new Ajv2020({ allErrors: true, strict: false })
  const ok = ajv.validate(schema(nome), dados)
  return ok ? null : JSON.stringify(ajv.errors)
}

describe("contrato com o pipeline (schemas/)", () => {
  it.each(ARQUIVOS)("fixture %s.json segue o schema", (nome) => {
    expect(validar(nome, ler(join(SITE, "src", "__fixtures__", `${nome}.json`)))).toBeNull()
  })

  it.each(ARQUIVOS)("dado publicado %s.json (se existir) segue o schema", (nome) => {
    const publicado = join(SITE, "public", "data", `${nome}.json`)
    if (!existsSync(publicado)) return
    expect(validar(nome, ler(publicado))).toBeNull()
  })
})
