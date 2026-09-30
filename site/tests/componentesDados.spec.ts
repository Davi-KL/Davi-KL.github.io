import { flushPromises } from "@vue/test-utils"
import { describe, expect, it, vi } from "vitest"
import { h } from "vue"
import DataTable from "../src/components/dados/DataTable.vue"
import EstadoDados from "../src/components/dados/EstadoDados.vue"
import PlotlyChart from "../src/components/dados/PlotlyChart.vue"
import { montar, texto } from "./montar"

const plotly = vi.hoisted(() => ({ react: vi.fn(async () => undefined), purge: vi.fn() }))
vi.mock("plotly.js-basic-dist-min", () => ({ default: plotly }))

describe("PlotlyChart", () => {
  it("desenha com o tema, a altura e o rótulo acessível", async () => {
    const w = await montar(PlotlyChart, { props: { dados: [{ type: "bar", x: [1] }], rotulo: "Gráfico de teste", altura: 420 } })
    await flushPromises()
    expect(w.attributes("role")).toBe("img")
    expect(w.attributes("aria-label")).toBe("Gráfico de teste")
    expect(plotly.react).toHaveBeenCalledTimes(1)
    const [, dados, layout, config] = plotly.react.mock.calls[0] as unknown as [HTMLElement, unknown[], Record<string, unknown>, Record<string, unknown>]
    expect(dados).toEqual([{ type: "bar", x: [1] }])
    expect(layout.height).toBe(420)
    expect(config.displaylogo).toBe(false)
  })

  it("redesenha quando os dados mudam e limpa ao desmontar", async () => {
    plotly.react.mockClear()
    const w = await montar(PlotlyChart, { props: { dados: [{ x: [1] }], rotulo: "g" } })
    await flushPromises()
    await w.setProps({ dados: [{ x: [2] }] })
    await flushPromises()
    expect(plotly.react).toHaveBeenCalledTimes(2)
    w.unmount()
    expect(plotly.purge).toHaveBeenCalled()
  })
})

describe("DataTable", () => {
  it("abre e fecha a tabela", async () => {
    const w = await montar(DataTable, { props: { colunas: ["UF", "Preço"], linhas: [["DF", "R$ 6,67"]], legenda: "Tabela" } })
    const botao = w.get("button")
    expect(botao.attributes("aria-expanded")).toBe("false")
    expect(w.find("table").exists()).toBe(false)
    await botao.trigger("click")
    expect(botao.attributes("aria-expanded")).toBe("true")
    expect(w.get("caption").text()).toBe("Tabela")
    expect(w.findAll("tbody tr")).toHaveLength(1)
    expect(botao.text()).toBe("Ocultar tabela")
  })
})

describe("EstadoDados", () => {
  const slots = { default: () => h("p", "conteúdo") }

  it("carregando", async () => {
    const w = await montar(EstadoDados, { props: { carregando: true, erro: false }, slots })
    expect(texto(w)).toContain("Carregando dados")
    expect(texto(w)).not.toContain("conteúdo")
  })

  it("erro mostra mensagem e link para o GitHub", async () => {
    const w = await montar(EstadoDados, { props: { carregando: false, erro: true }, slots })
    expect(texto(w)).toContain("Dados indisponíveis no momento.")
    expect(w.find("a[href='https://github.com/Davi-KL/Davi-KL.github.io']").exists()).toBe(true)
  })

  it("pronto mostra o conteúdo", async () => {
    const w = await montar(EstadoDados, { props: { carregando: false, erro: false }, slots })
    expect(texto(w)).toContain("conteúdo")
  })
})
