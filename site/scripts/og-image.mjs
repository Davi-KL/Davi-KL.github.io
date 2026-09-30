import { fileURLToPath } from "node:url"
import sharp from "sharp"

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#0f172a"/>
  <text x="80" y="140" font-family="Arial, Helvetica, sans-serif" font-size="40" fill="#94a3b8">Davi Levy</text>
  <text x="80" y="250" font-family="Arial, Helvetica, sans-serif" font-size="76" font-weight="700" fill="#f8fafc">Código que resolve.</text>
  <text x="80" y="345" font-family="Arial, Helvetica, sans-serif" font-size="76" font-weight="700" fill="#38bdf8">Dados que explicam.</text>
  <text x="80" y="420" font-family="Arial, Helvetica, sans-serif" font-size="32" fill="#94a3b8">Full Stack · C#/.NET · Vue · Python/Pandas</text>
  <polyline points="80,560 240,548 400,552 560,522 720,532 880,492 1040,502 1120,470" fill="none" stroke="#38bdf8" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="80,575 240,566 400,570 560,545 720,550 880,515 1040,520 1120,498" fill="none" stroke="#f59e0b" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`

const destino = fileURLToPath(new URL("../public/og-image.png", import.meta.url))
await sharp(Buffer.from(svg)).png().toFile(destino)
console.log(`gerado: ${destino}`)
