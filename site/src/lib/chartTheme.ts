import type { Produto } from "../types/dados"

export const CORES_PRODUTO: Record<Produto, string> = {
  gasolina: "#38bdf8",
  etanol: "#34d399",
  diesel_s10: "#a78bfa",
}
export const COR_DESTAQUE = "#f59e0b"
export const COR_REFERENCIA = "#e2e8f0"

const EIXO = { gridcolor: "#1e293b", zerolinecolor: "#334155", linecolor: "#334155", tickcolor: "#334155" }

export const LAYOUT_BASE = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { family: "Inter Variable, Inter, system-ui, sans-serif", color: "#e2e8f0", size: 13 },
  margin: { l: 56, r: 16, t: 16, b: 48 },
  xaxis: EIXO,
  yaxis: EIXO,
  legend: { orientation: "h", y: -0.18 },
  hoverlabel: { bgcolor: "#1e293b", bordercolor: "#334155", font: { color: "#e2e8f0" } },
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
