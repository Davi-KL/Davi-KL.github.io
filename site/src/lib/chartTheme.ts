import type { Produto } from "../types/dados"

export const CORES_PRODUTO: Record<Produto, string> = {
  gasolina: "#6cc7f0",
  etanol: "#5fd39a",
  diesel_s10: "#ff8a7a",
}
export const COR_DESTAQUE = "#ffb020"
export const COR_REFERENCIA = "#d9dee7"

const EIXO = { gridcolor: "#1d2430", zerolinecolor: "#2a3240", linecolor: "#2a3240", tickcolor: "#2a3240" }

export const LAYOUT_BASE = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { family: "Instrument Sans Variable, Instrument Sans, system-ui, sans-serif", color: "#d9dee7", size: 13 },
  margin: { l: 56, r: 16, t: 16, b: 48 },
  xaxis: EIXO,
  yaxis: EIXO,
  legend: { orientation: "h", y: -0.18 },
  hoverlabel: { bgcolor: "#161b23", bordercolor: "#2a3240", font: { color: "#d9dee7" } },
}

export const CONFIG_BASE = {
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
}

function objeto(valor: unknown): Record<string, unknown> {
  return typeof valor === "object" && valor !== null ? (valor as Record<string, unknown>) : {}
}

export function mesclarLayout(extra: Record<string, unknown>, altura: number): Record<string, unknown> {
  return {
    ...LAYOUT_BASE,
    ...extra,
    height: altura,
    xaxis: { ...EIXO, ...objeto(extra.xaxis) },
    yaxis: { ...EIXO, ...objeto(extra.yaxis) },
  }
}
