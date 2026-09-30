type Idioma = "pt" | "en"

const LOCALE: Record<Idioma, string> = { pt: "pt-BR", en: "en-US" }

function utc(iso: string): Date {
  const [ano, mes, dia = 1] = iso.split("-").map(Number)
  return new Date(Date.UTC(ano, mes - 1, dia))
}

export function formatarReais(valor: number, idioma: Idioma): string {
  return new Intl.NumberFormat(LOCALE[idioma], { style: "currency", currency: "BRL" }).format(valor)
}

export function formatarPct(valor: number, idioma: Idioma, casas = 1): string {
  return new Intl.NumberFormat(LOCALE[idioma], {
    style: "percent",
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
    signDisplay: "exceptZero",
  }).format(valor / 100)
}

export function formatarRazao(valor: number, idioma: Idioma): string {
  return new Intl.NumberFormat(LOCALE[idioma], {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(valor)
}

export function formatarNumero(valor: number, idioma: Idioma): string {
  return new Intl.NumberFormat(LOCALE[idioma]).format(valor)
}

export function formatarData(iso: string, idioma: Idioma): string {
  const opcoes: Intl.DateTimeFormatOptions =
    idioma === "pt"
      ? { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" }
      : { dateStyle: "medium", timeZone: "UTC" }
  return new Intl.DateTimeFormat(LOCALE[idioma], opcoes).format(utc(iso))
}

export function formatarDiaMes(iso: string, idioma: Idioma): string {
  const opcoes: Intl.DateTimeFormatOptions =
    idioma === "pt"
      ? { day: "2-digit", month: "2-digit", timeZone: "UTC" }
      : { month: "short", day: "numeric", timeZone: "UTC" }
  return new Intl.DateTimeFormat(LOCALE[idioma], opcoes).format(utc(iso))
}

export function formatarMes(mes: string, idioma: Idioma): string {
  return new Intl.DateTimeFormat(LOCALE[idioma], { month: "2-digit", year: "numeric", timeZone: "UTC" }).format(utc(mes))
}
