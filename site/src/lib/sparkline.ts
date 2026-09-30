export type Serie = readonly (number | null)[]

export function dominio(series: readonly Serie[]): [number, number] | null {
  const valores = series.flat().filter((v): v is number => v !== null)
  return valores.length ? [Math.min(...valores), Math.max(...valores)] : null
}

export function caminhoSparkline(valores: Serie, largura: number, altura: number, dom: [number, number], margem = 4): string {
  if (valores.length < 2) return ""
  const [min, max] = dom
  const faixa = max - min || 1
  const passo = (largura - 2 * margem) / (valores.length - 1)
  const partes: string[] = []
  let emTraco = false
  valores.forEach((v, i) => {
    if (v === null) {
      emTraco = false
      return
    }
    const x = margem + i * passo
    const y = altura - margem - ((v - min) / faixa) * (altura - 2 * margem)
    partes.push(`${emTraco ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`)
    emTraco = true
  })
  return partes.join(" ")
}
