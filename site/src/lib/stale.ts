const DIA_MS = 86_400_000

export function diasDesde(iso: string, agora: Date): number {
  const [ano, mes, dia] = iso.split("-").map(Number)
  return Math.floor((agora.getTime() - Date.UTC(ano, mes - 1, dia)) / DIA_MS)
}

export function dadosDesatualizados(semanaMaisRecente: string, agora: Date, limiteDias = 21): boolean {
  return diasDesde(semanaMaisRecente, agora) > limiteDias
}
