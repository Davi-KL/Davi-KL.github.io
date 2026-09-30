declare module "plotly.js-basic-dist-min" {
  interface PlotlyBasico {
    react(
      elemento: HTMLElement,
      dados: unknown[],
      layout?: Record<string, unknown>,
      config?: Record<string, unknown>,
    ): Promise<unknown>
    purge(elemento: HTMLElement): void
  }
  const Plotly: PlotlyBasico
  export default Plotly
}
