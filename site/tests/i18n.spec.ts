import { describe, expect, it } from "vitest"
import en from "../src/content/en.json"
import pt from "../src/content/pt.json"
import { projetos } from "../src/content/perfil"
import { idiomaInicial } from "../src/i18n"

function folhas(obj: unknown, prefixo = ""): [string, unknown][] {
  if (Array.isArray(obj)) return obj.flatMap((v, i) => folhas(v, `${prefixo}[${i}]`))
  if (obj && typeof obj === "object") {
    return Object.entries(obj).flatMap(([k, v]) => folhas(v, prefixo ? `${prefixo}.${k}` : k))
  }
  return [[prefixo, obj]]
}

describe("conteúdo bilíngue", () => {
  it("pt e en têm exatamente as mesmas chaves", () => {
    expect(folhas(en).map(([k]) => k)).toEqual(folhas(pt).map(([k]) => k))
  })

  it("mensagens da ui usam os mesmos parâmetros nos dois idiomas", () => {
    const params = (s: unknown) => [...String(s).matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort()
    const enPorChave = new Map(folhas(en.ui))
    for (const [chave, valor] of folhas(pt.ui)) {
      expect(params(enPorChave.get(chave)), chave).toEqual(params(valor))
    }
  })

  it("mensagens da ui não usam caracteres especiais do vue-i18n", () => {
    for (const [chave, valor] of [...folhas(pt.ui), ...folhas(en.ui)]) {
      expect(String(valor), chave).not.toMatch(/[@$|]/)
    }
  })

  it("todo projeto tem título, descrição e papel nos dois idiomas", () => {
    for (const p of projetos) {
      for (const idioma of [pt, en]) {
        const item = idioma.conteudo.projetos.itens[p.id]
        expect(item.titulo.length).toBeGreaterThan(0)
        expect(item.descricao.length).toBeGreaterThan(20)
        expect(item.papel.length).toBeGreaterThan(0)
      }
    }
    expect(projetos.map((p) => p.id)).toEqual(["nodus", "forunb", "soma", "anp", "flowpad", "compiladores"])
  })
})

describe("idiomaInicial", () => {
  it("usa o idioma salvo primeiro", () => {
    expect(idiomaInicial(["pt-BR"], "en")).toBe("en")
  })
  it("segue a primeira língua do navegador", () => {
    expect(idiomaInicial(["pt-BR", "en"], null)).toBe("pt")
    expect(idiomaInicial(["en-US", "pt-BR"], null)).toBe("en")
    expect(idiomaInicial(["es-ES"], null)).toBe("en")
  })
  it("sem informação usa português", () => {
    expect(idiomaInicial([], null)).toBe("pt")
    expect(idiomaInicial([], "fr")).toBe("pt")
  })
})
