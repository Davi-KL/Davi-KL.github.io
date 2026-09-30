import { mkdir, readFile, writeFile } from "node:fs/promises"

const dist = new URL("../dist/", import.meta.url)
const html = await readFile(new URL("index.html", dist), "utf8")

// Qualquer rota desconhecida: o GitHub Pages serve 404.html, que carrega o app.
await writeFile(new URL("404.html", dist), html)

// /dados-combustiveis/ ganha um index.html próprio (status 200 e metadados da página).
const titulo = "Preços dos combustíveis no Brasil — Davi Levy"
const descricao = "Análise interativa dos preços de gasolina, etanol e diesel desde 2004, com dados da ANP atualizados toda semana."
const url = "https://davi-kl.github.io/dados-combustiveis/"
const trocas = [
  [/<title>[^<]*<\/title>/, `<title>${titulo}</title>`],
  [/(<meta name="description" content=")[^"]*(")/, `$1${descricao}$2`],
  [/(<meta property="og:title" content=")[^"]*(")/, `$1${titulo}$2`],
  [/(<meta property="og:description" content=")[^"]*(")/, `$1${descricao}$2`],
  [/(<meta property="og:url" content=")[^"]*(")/, `$1${url}$2`],
  [/(<link rel="canonical" href=")[^"]*(")/, `$1${url}$2`],
]
let dados = html
for (const [padrao, valor] of trocas) {
  if (!padrao.test(dados)) throw new Error(`spa-fallback: padrão não encontrado no index.html: ${padrao}`)
  dados = dados.replace(padrao, valor)
}
await mkdir(new URL("dados-combustiveis/", dist), { recursive: true })
await writeFile(new URL("dados-combustiveis/index.html", dist), dados)
console.log("spa-fallback: 404.html e dados-combustiveis/index.html gerados")
