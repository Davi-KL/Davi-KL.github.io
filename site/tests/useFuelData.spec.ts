import { flushPromises } from "@vue/test-utils"
import { beforeEach, describe, expect, it } from "vitest"
import meta from "../src/__fixtures__/meta.json"
import { carregarJson, limparCacheDados, useFuelData } from "../src/composables/useFuelData"
import { simularDados } from "./montar"

describe("useFuelData", () => {
  beforeEach(() => limparCacheDados())

  it("carrega o JSON da pasta data/", async () => {
    const fetch = simularDados({ "meta.json": meta })
    const estado = useFuelData("meta.json")
    expect(estado.carregando.value).toBe(true)
    await flushPromises()
    expect(estado.dados.value).toEqual(meta)
    expect(estado.erro.value).toBe(false)
    expect(estado.carregando.value).toBe(false)
    expect(fetch).toHaveBeenCalledWith("/data/meta.json")
  })

  it("marca erro em 404", async () => {
    simularDados({})
    const estado = useFuelData("evolucao.json")
    await flushPromises()
    expect(estado.erro.value).toBe(true)
    expect(estado.dados.value).toBeNull()
  })

  it("marca erro quando a rede falha", async () => {
    simularDados({ "meta.json": "rede" })
    const estado = useFuelData("meta.json")
    await flushPromises()
    expect(estado.erro.value).toBe(true)
  })

  it("busca cada arquivo uma vez só", async () => {
    const fetch = simularDados({ "meta.json": meta })
    await Promise.all([carregarJson("meta.json"), carregarJson("meta.json")])
    expect(fetch).toHaveBeenCalledTimes(1)
  })

  it("tenta de novo depois de um erro", async () => {
    const fetch = simularDados({ "meta.json": 500 })
    await expect(carregarJson("meta.json")).rejects.toThrow("HTTP 500")
    await expect(carregarJson("meta.json")).rejects.toThrow()
    expect(fetch).toHaveBeenCalledTimes(2)
  })
})
