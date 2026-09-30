import { describe, expect, it } from "vitest"
import { createMemoryHistory } from "vue-router"
import { criarRouter } from "../src/router"

describe("rotas", () => {
  it("home e página de dados", async () => {
    const router = criarRouter(createMemoryHistory())
    await router.push("/dados-combustiveis")
    expect(router.currentRoute.value.name).toBe("dados")
    await router.push("/")
    expect(router.currentRoute.value.name).toBe("home")
  })

  it("aceita barra final (GitHub Pages serve /dados-combustiveis/)", async () => {
    const router = criarRouter(createMemoryHistory())
    await router.push("/dados-combustiveis/")
    expect(router.currentRoute.value.name).toBe("dados")
  })

  it("rota desconhecida volta para a home", async () => {
    const router = criarRouter(createMemoryHistory())
    await router.push("/nao-existe")
    expect(router.currentRoute.value.path).toBe("/")
  })
})
