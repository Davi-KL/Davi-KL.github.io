# Site do Portfólio — Plano de Implementação (Parte 2 de 2)

> **Para agentes:** SUB-SKILL OBRIGATÓRIA: use superpowers:subagent-driven-development (recomendado) ou superpowers:executing-plans para implementar este plano tarefa por tarefa. Os passos usam checkbox (`- [ ]`) para acompanhamento.

**Objetivo:** construir o site do portfólio em Vue 3, com a home e a página `/dados-combustiveis`, bilíngue (PT/EN), consumindo os JSONs do pipeline, e publicá-lo no GitHub Pages com deploy automático.

**Arquitetura:** SPA em Vue 3 + Vite + TypeScript, com duas rotas.
- **Textos:** ficam em `src/content/{pt,en}.json`. A chave `ui` guarda os textos curtos, que passam pelo vue-i18n. A chave `conteudo` guarda os textos longos, lidos diretamente por `useConteudo()`.
- **Dados:** o site só lê os arquivos de `public/data/`, com os tipos espelhados de `schemas/`.
- **Separação da lógica:** a lógica de gráficos, formatação e insights fica em funções puras em `src/lib/`, testáveis sem DOM. Os componentes só as montam.
- **Plotly:** é carregado só quando um gráfico entra na tela, via import dinâmico.

**Tecnologias:** Vue 3, Vite, TypeScript, vue-router, vue-i18n, plotly.js-basic-dist-min, @fontsource-variable/inter, Vitest, @vue/test-utils, jsdom, Ajv, ESLint, sharp (só para gerar a imagem OG).

**Spec:** `docs/superpowers/specs/2026-09-30-portfolio-design.md`, seções 5, 6.1, 7, 8 e 9.

**Pré-requisito:** a Parte 1 (`docs/superpowers/plans/2026-09-30-pipeline-anp.md`) concluída até a Tarefa 11. Isso significa que `schemas/*.schema.json` e `site/public/data/*.json` já existem. As Tarefas 1 a 10 deste plano funcionam só com os fixtures e podem começar assim que os schemas (Parte 1, Tarefa 9) existirem.

## Restrições globais

- Todos os comandos rodam no Git Bash, a partir de `site/` (`cd site`), salvo quando indicado.
- Node ≥ 20.19 (local: 24; CI: 22). As versões das dependências são as resolvidas pelo `npm install` da Tarefa 1 e ficam travadas no `package-lock.json`.
- URL pública: `https://davi-kl.github.io/`, repositório `Davi-KL/Davi-KL.github.io`, `base` do Vite igual a `/`.
- Rotas: `/` (home) e `/dados-combustiveis`. Qualquer outra redireciona para `/`.
- Dados: `import.meta.env.BASE_URL + "data/" + arquivo`, com os arquivos `meta.json`, `evolucao.json`, `ranking_uf.json` e `etanol_gasolina.json`.
- Textos da chave `ui` **não podem conter** `@`, `$` nem `|`, porque são sintaxe do vue-i18n. Preços como "R$ 6,67" entram sempre como parâmetro já formatado. E-mails e URLs ficam em `src/content/perfil.ts`, nunca nos JSONs de idioma.
- Cores (tokens em `src/styles/tokens.css`):
  - fundo `#0f172a`, superfície `#1e293b`, borda `#334155`;
  - texto `#e2e8f0`, texto forte `#f8fafc`, texto suave `#94a3b8`;
  - azul `#38bdf8`, violeta `#a78bfa`, verde `#34d399`, âmbar `#f59e0b`.
- Cor fixa por produto em todos os gráficos: gasolina `#38bdf8`, etanol `#34d399`, diesel S10 `#a78bfa`. UF em destaque: `#f59e0b`. Linhas de referência: `#e2e8f0`, tracejadas.
- E-mail `daviklevy@gmail.com`, LinkedIn `https://www.linkedin.com/in/davi-levy-dev`, GitHub `https://github.com/Davi-KL`.
- O botão de CV só aparece quando `cv[idioma]` em `src/content/perfil.ts` não é `null`.
- Áreas clicáveis com pelo menos 44 px de altura. Foco sempre visível. Contraste de texto AA.
- Mensagens de commit terminam com a linha `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Foco de revisão

1. **Um JSON de dados que falha ou atrasa** (404, rede fora, JSON parcial). A seção correspondente mostra "Dados indisponíveis no momento" e as outras continuam funcionando. Na home, a prévia e o número de gasolina do hero somem sem deixar buraco. Testes nas Tarefas 3, 5, 7 e 10.
2. **Troca de idioma com a página aberta.** Todos os textos, formatos de número e data e rótulos de gráfico mudam juntos, e a escolha fica salva. A paridade de chaves e parâmetros entre PT e EN é testada. Testes nas Tarefas 2 e 4.
3. **Abrir `/dados-combustiveis` direto** (link compartilhado, F5) no GitHub Pages. A página precisa responder com status 200 e metadados próprios, e não com o 404 genérico. Verificação na Tarefa 11.
4. **Séries com buracos** (`null`, como o diesel S10 antes de 2013 ou uma UF sem coleta num mês). O minigráfico interrompe a linha, a tabela mostra "—" e os insights ignoram os buracos. Testes nas Tarefas 7 e 8.
5. **Dados antigos** (o workflow semanal falhou várias vezes). Com mais de 21 dias desde a semana mais recente, aparece o aviso "dados de DD/MM". Teste na Tarefa 10.

---

### Tarefa 1: Projeto Vite + estilos base + formatação

**Arquivos:**
- Criar: `site/package.json`, `site/vite.config.ts`, `site/tsconfig.json`, `site/eslint.config.js`, `site/index.html`
- Criar: `site/src/styles/tokens.css`, `site/src/styles/base.css`
- Criar: `site/src/lib/format.ts`
- Criar: `site/tests/setup.ts`, `site/tests/format.spec.ts`

**Interfaces:**
- Produz (`src/lib/format.ts`), com `Idioma = "pt" | "en"` exportado de `src/i18n.ts` (Tarefa 2). Nesta tarefa, `format.ts` declara o próprio tipo local.
  - `formatarReais(valor: number, idioma): string`, no formato "R$ 6,67" / "R$6.67".
  - `formatarPct(valor: number, idioma, casas = 1): string`, que recebe o valor em pontos percentuais: `1.7` vira "+1,7%".
  - `formatarRazao(valor: number, idioma): string`: `0.657` vira "65,7%".
  - `formatarData(iso: "AAAA-MM-DD", idioma)`: "21/09/2026" / "Sep 21, 2026".
  - `formatarDiaMes(iso, idioma)`: "21/09" / "Sep 21".
  - `formatarMes("AAAA-MM", idioma)`: "08/2026".
  - `formatarNumero(valor: number, idioma)`: "420.419" / "420,419".

- [ ] **Passo 1: Criar o `package.json` e instalar as dependências**

`site/package.json`:

```json
{
  "name": "portfolio-davi-levy",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build && node scripts/spa-fallback.mjs",
    "preview": "vite preview",
    "test": "vitest run",
    "lint": "eslint . --max-warnings=0 && vue-tsc --noEmit",
    "og": "node scripts/og-image.mjs"
  }
}
```

```bash
cd site
npm install vue vue-router vue-i18n plotly.js-basic-dist-min @fontsource-variable/inter
npm install -D vite @vitejs/plugin-vue typescript vue-tsc vitest @vue/test-utils jsdom @types/node ajv eslint @eslint/js typescript-eslint eslint-plugin-vue globals sharp
```

Esperado: `added N packages` e o `package.json` passa a listar as dependências.

- [ ] **Passo 2: Criar as configurações**

`site/vite.config.ts`:

```ts
/// <reference types="vitest/config" />
import vue from "@vitejs/plugin-vue"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [vue()],
  base: "/",
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
  build: { chunkSizeWarningLimit: 1500 },
  test: {
    environment: "jsdom",
    include: ["tests/**/*.spec.ts"],
    setupFiles: ["tests/setup.ts"],
    restoreMocks: true,
    unstubGlobals: true,
  },
})
```

`site/tests/setup.ts`:

```ts
// O jsdom não implementa rolagem, e o scrollBehavior do vue-router chama window.scrollTo.
window.scrollTo = (() => {}) as typeof window.scrollTo
```

`site/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noEmit": true,
    "jsx": "preserve",
    "types": ["vite/client", "node"]
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "tests/**/*.ts", "vite.config.ts"]
}
```

`site/eslint.config.js`:

```js
import js from "@eslint/js"
import vue from "eslint-plugin-vue"
import globals from "globals"
import tseslint from "typescript-eslint"

export default tseslint.config(
  { ignores: ["dist/**", "node_modules/**", "public/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...vue.configs["flat/essential"],
  {
    files: ["**/*.vue"],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
  },
  {
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  },
)
```

`site/index.html`:

```html
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Davi Levy — Desenvolvedor Full Stack · Dados</title>
    <meta name="description" content="Portfólio de Davi Levy: desenvolvimento full stack (C#/.NET, Vue, TypeScript) e análise de dados." />
    <meta name="theme-color" content="#0f172a" />
    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
    <link rel="canonical" href="https://davi-kl.github.io/" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Davi Levy" />
    <meta property="og:title" content="Davi Levy — Desenvolvedor Full Stack · Dados" />
    <meta property="og:description" content="Portfólio de Davi Levy: desenvolvimento full stack (C#/.NET, Vue, TypeScript) e análise de dados." />
    <meta property="og:url" content="https://davi-kl.github.io/" />
    <meta property="og:image" content="https://davi-kl.github.io/og-image.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:locale" content="pt_BR" />
    <meta name="twitter:card" content="summary_large_image" />
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Passo 3: Criar os estilos base**

`site/src/styles/tokens.css`:

```css
:root {
  --cor-fundo: #0f172a;
  --cor-superficie: #1e293b;
  --cor-borda: #334155;
  --cor-texto: #e2e8f0;
  --cor-texto-forte: #f8fafc;
  --cor-texto-suave: #94a3b8;
  --cor-azul: #38bdf8;
  --cor-violeta: #a78bfa;
  --cor-verde: #34d399;
  --cor-ambar: #f59e0b;
  --fonte: "Inter Variable", Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
  --raio: 12px;
  --largura-max: 1120px;
  color-scheme: dark;
}
```

`site/src/styles/base.css`:

```css
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--cor-fundo);
  color: var(--cor-texto);
  font-family: var(--fonte);
  font-size: 1rem;
  line-height: 1.6;
}
img, svg { max-width: 100%; display: block; }
a { color: var(--cor-azul); text-underline-offset: 3px; }
a:hover { color: var(--cor-texto-forte); }
:focus-visible { outline: 3px solid var(--cor-azul); outline-offset: 3px; border-radius: 4px; }
[id] { scroll-margin-top: 80px; }
h1, h2, h3 { color: var(--cor-texto-forte); line-height: 1.2; margin: 0 0 0.5em; }
h1 { font-size: clamp(2rem, 6vw, 3.5rem); letter-spacing: -0.02em; }
h2 { font-size: clamp(1.5rem, 3vw, 2rem); }
h3 { font-size: 1.125rem; }
p { margin: 0 0 1em; }

.container { width: 100%; max-width: var(--largura-max); margin-inline: auto; padding-inline: 16px; }
@media (min-width: 640px) { .container { padding-inline: 24px; } }
.secao { padding-block: clamp(3rem, 8vw, 5rem); border-top: 1px solid var(--cor-borda); }
.secao__subtitulo { color: var(--cor-texto-suave); max-width: 65ch; }
.cartao { background: var(--cor-superficie); border: 1px solid var(--cor-borda); border-radius: var(--raio); padding: 1.25rem; }
.suave { color: var(--cor-texto-suave); }

.botao {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  min-height: 44px; padding: 0.625rem 1.125rem;
  border-radius: 999px; border: 1px solid var(--cor-azul);
  background: var(--cor-azul); color: var(--cor-fundo);
  font: inherit; font-weight: 600; text-decoration: none; cursor: pointer;
}
.botao:hover { background: var(--cor-texto-forte); border-color: var(--cor-texto-forte); color: var(--cor-fundo); }
.botao--secundario { background: transparent; color: var(--cor-texto-forte); border-color: var(--cor-borda); }
.botao--secundario:hover { background: var(--cor-superficie); color: var(--cor-texto-forte); border-color: var(--cor-texto-suave); }
.botao[aria-pressed="true"] { background: var(--cor-azul); color: var(--cor-fundo); border-color: var(--cor-azul); }

.etiquetas { display: flex; flex-wrap: wrap; gap: 0.5rem; list-style: none; padding: 0; margin: 0; }
.etiquetas li { font-size: 0.8125rem; padding: 0.125rem 0.625rem; border: 1px solid var(--cor-borda); border-radius: 999px; }

.pular {
  position: absolute; left: 16px; top: -100px; z-index: 100;
  background: var(--cor-azul); color: var(--cor-fundo);
  padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600;
}
.pular:focus { top: 16px; }

.controles { display: flex; flex-wrap: wrap; gap: 0.75rem 1.25rem; align-items: end; margin-bottom: 1rem; }
.controles label { display: grid; gap: 0.25rem; font-size: 0.875rem; color: var(--cor-texto-suave); }
select {
  min-height: 44px; min-width: 10rem; padding: 0.5rem 0.75rem;
  border-radius: 8px; border: 1px solid var(--cor-borda);
  background: var(--cor-superficie); color: var(--cor-texto-forte); font: inherit;
}
table { width: 100%; border-collapse: collapse; font-size: 0.875rem; font-variant-numeric: tabular-nums; }
caption { text-align: left; color: var(--cor-texto-suave); padding-bottom: 0.5rem; }
th, td { padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--cor-borda); text-align: left; }
th { color: var(--cor-texto-forte); position: sticky; top: 0; background: var(--cor-superficie); }

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
```

- [ ] **Passo 4: Escrever o teste que falha**

`site/tests/format.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import {
  formatarData,
  formatarDiaMes,
  formatarMes,
  formatarNumero,
  formatarPct,
  formatarRazao,
  formatarReais,
} from "../src/lib/format"

const normal = (s: string) => s.replace(/\s/g, " ")

describe("formatação", () => {
  it("reais", () => {
    expect(normal(formatarReais(6.669, "pt"))).toBe("R$ 6,67")
    expect(formatarReais(6.669, "en")).toBe("R$6.67")
  })
  it("percentual com sinal, em pontos percentuais", () => {
    expect(formatarPct(1.7, "pt")).toBe("+1,7%")
    expect(formatarPct(-2.5, "en")).toBe("-2.5%")
    expect(formatarPct(0, "pt")).toBe("0,0%")
  })
  it("razão", () => {
    expect(formatarRazao(0.657, "pt")).toBe("65,7%")
    expect(formatarRazao(0.657, "en")).toBe("65.7%")
  })
  it("datas sem deslocamento de fuso", () => {
    expect(formatarData("2026-09-21", "pt")).toBe("21/09/2026")
    expect(formatarData("2026-09-21", "en")).toBe("Sep 21, 2026")
    expect(formatarDiaMes("2026-09-21", "pt")).toBe("21/09")
    expect(formatarDiaMes("2026-09-21", "en")).toBe("Sep 21")
    expect(formatarMes("2026-08", "pt")).toBe("08/2026")
  })
  it("números inteiros", () => {
    expect(formatarNumero(420419, "pt")).toBe("420.419")
    expect(formatarNumero(420419, "en")).toBe("420,419")
  })
})
```

- [ ] **Passo 5: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/format.spec.ts`
Esperado: FALHA com `Failed to resolve import "../src/lib/format"`.

- [ ] **Passo 6: Implementar `format.ts`**

`site/src/lib/format.ts`:

```ts
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
```

- [ ] **Passo 7: Rodar e ver passar**

Rodar: `cd site && npx vitest run tests/format.spec.ts`
Esperado: 5 passed.

- [ ] **Passo 8: Commit**

```bash
cd site
git add package.json package-lock.json vite.config.ts tsconfig.json eslint.config.js index.html src/styles src/lib/format.ts tests/setup.ts tests/format.spec.ts
git commit -m "feat(site): projeto Vite, estilos base e formatação" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 2: Idiomas, conteúdo e perfil

**Arquivos:**
- Criar: `site/src/i18n.ts`
- Criar: `site/src/content/pt.json`, `site/src/content/en.json`
- Criar: `site/src/content/perfil.ts`
- Criar: `site/src/composables/useConteudo.ts`
- Modificar: `site/src/lib/format.ts`, trocando a linha `type Idioma = "pt" | "en"` por `import type { Idioma } from "../i18n"`
- Criar: `site/tests/i18n.spec.ts`

**Interfaces:**
- Produz:
  - `src/i18n.ts`:
    - `type Idioma = "pt" | "en"`;
    - `idiomaInicial(linguas?: readonly string[], salvo?: string | null): Idioma`;
    - `i18n`, criado com `createI18n({ legacy: false })` e mensagens `pt.ui` / `en.ui`;
    - `aplicarLang(idioma): void`, que define `<html lang>`;
    - `definirIdioma(idioma): void`, que troca o idioma, aplica o `lang` e salva em `localStorage["idioma"]`.
  - `src/composables/useConteudo.ts`: `type Conteudo = typeof pt.conteudo` e `useConteudo(): ComputedRef<Conteudo>`.
  - `src/content/perfil.ts`:
    - `perfil`, com `nome`, `email`, `linkedin`, `github`, `repositorios`, `codigoPipeline` e `repoPortfolio`;
    - `cv: Record<Idioma, string | null>`;
    - `stack` e `type GrupoStack`;
    - `type ProjetoId`, `type TipoLink`, `interface Projeto` e `projetos: Projeto[]`, com 6 projetos.

- [ ] **Passo 1: Escrever o teste que falha**

`site/tests/i18n.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import en from "../src/content/en.json"
import pt from "../src/content/pt.json"
import { projetos } from "../src/content/perfil"
import { idiomaInicial } from "../src/i18n"

function folhas(obj: unknown, prefixo = ""): [string, unknown][] {
  if (Array.isArray(obj)) return obj.flatMap((v, i) => folhas(v, `${prefixo}[${i}]`))
  if (obj && typeof obj === "object") {
    return Object.entries(obj).flatMap(([k, v]) => folhas(v, prefixo ? `${prefixo}.${k}` : k))
  }
  return [[prefixo, obj]]
}

describe("conteúdo bilíngue", () => {
  it("pt e en têm exatamente as mesmas chaves", () => {
    expect(folhas(en).map(([k]) => k)).toEqual(folhas(pt).map(([k]) => k))
  })

  it("mensagens da ui usam os mesmos parâmetros nos dois idiomas", () => {
    const params = (s: unknown) => [...String(s).matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort()
    const enPorChave = new Map(folhas(en.ui))
    for (const [chave, valor] of folhas(pt.ui)) {
      expect(params(enPorChave.get(chave)), chave).toEqual(params(valor))
    }
  })

  it("mensagens da ui não usam caracteres especiais do vue-i18n", () => {
    for (const [chave, valor] of [...folhas(pt.ui), ...folhas(en.ui)]) {
      expect(String(valor), chave).not.toMatch(/[@$|]/)
    }
  })

  it("todo projeto tem título, descrição e papel nos dois idiomas", () => {
    for (const p of projetos) {
      for (const idioma of [pt, en]) {
        const item = idioma.conteudo.projetos.itens[p.id]
        expect(item.titulo.length).toBeGreaterThan(0)
        expect(item.descricao.length).toBeGreaterThan(20)
        expect(item.papel.length).toBeGreaterThan(0)
      }
    }
    expect(projetos.map((p) => p.id)).toEqual(["nodus", "forunb", "soma", "anp", "flowpad", "compiladores"])
  })
})

describe("idiomaInicial", () => {
  it("usa o idioma salvo primeiro", () => {
    expect(idiomaInicial(["pt-BR"], "en")).toBe("en")
  })
  it("segue a primeira língua do navegador", () => {
    expect(idiomaInicial(["pt-BR", "en"], null)).toBe("pt")
    expect(idiomaInicial(["en-US", "pt-BR"], null)).toBe("en")
    expect(idiomaInicial(["es-ES"], null)).toBe("en")
  })
  it("sem informação usa português", () => {
    expect(idiomaInicial([], null)).toBe("pt")
    expect(idiomaInicial([], "fr")).toBe("pt")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/i18n.spec.ts`
Esperado: FALHA com `Failed to resolve import "../src/content/en.json"`.

- [ ] **Passo 3: Criar `src/i18n.ts`**

```ts
import { createI18n } from "vue-i18n"
import en from "./content/en.json"
import pt from "./content/pt.json"

export type Idioma = "pt" | "en"

const CHAVE = "idioma"

function lerLinguas(): readonly string[] {
  if (typeof navigator === "undefined") return []
  return navigator.languages?.length ? navigator.languages : [navigator.language]
}

function lerSalvo(): string | null {
  try {
    return localStorage.getItem(CHAVE)
  } catch {
    return null
  }
}

export function idiomaInicial(linguas: readonly string[] = lerLinguas(), salvo: string | null = lerSalvo()): Idioma {
  if (salvo === "pt" || salvo === "en") return salvo
  const primeira = linguas[0]?.toLowerCase()
  return !primeira || primeira.startsWith("pt") ? "pt" : "en"
}

export const i18n = createI18n({
  legacy: false,
  locale: idiomaInicial(),
  fallbackLocale: "pt",
  messages: { pt: pt.ui, en: en.ui },
})

export function aplicarLang(idioma: Idioma): void {
  document.documentElement.lang = idioma === "pt" ? "pt-BR" : "en"
}

export function definirIdioma(idioma: Idioma): void {
  i18n.global.locale.value = idioma
  aplicarLang(idioma)
  try {
    localStorage.setItem(CHAVE, idioma)
  } catch {
    // navegação privada: segue sem salvar
  }
}
```

- [ ] **Passo 4: Criar `src/content/perfil.ts`**

```ts
import type { Idioma } from "../i18n"

export const perfil = {
  nome: "Davi Levy",
  email: "daviklevy@gmail.com",
  linkedin: "https://www.linkedin.com/in/davi-levy-dev",
  github: "https://github.com/Davi-KL",
  repositorios: "https://github.com/Davi-KL?tab=repositories",
  codigoPipeline: "https://github.com/Davi-KL/Davi-KL.github.io/tree/main/pipeline",
  repoPortfolio: "https://github.com/Davi-KL/Davi-KL.github.io",
}

/**
 * Caminho do CV por idioma. Fica `null` (botão oculto) até o PDF sem endereço e
 * telefone ser colocado em `public/cv/` — então vira "/cv/cv-pt.pdf" ou "/cv/cv-en.pdf".
 */
export const cv: Record<Idioma, string | null> = { pt: null, en: null }

export const stack = {
  front: ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "Quasar"],
  back: ["C#", "ASP.NET MVC", ".NET Core/Framework", "Python", "Django", "Node/Express", "SQL", "PostgreSQL", "PL/SQL (Oracle)", "SQLite"],
  dados: ["Pandas", "NumPy", "Scikit-learn", "Matplotlib", "Plotly", "Seaborn"],
  devops: ["Docker", "Git", "GitHub Actions", "Azure DevOps", "Linux", "Electron"],
}

export type GrupoStack = keyof typeof stack
export type ProjetoId = "nodus" | "forunb" | "soma" | "anp" | "flowpad" | "compiladores"
export type TipoLink = "codigo" | "documentacao" | "analise"

export interface Projeto {
  id: ProjetoId
  tags: string[]
  links: { tipo: TipoLink; url: string; interno?: boolean }[]
}

export const projetos: Projeto[] = [
  {
    id: "nodus",
    tags: ["Angular", "TypeScript", "Express", "SQLite", "Electron", "AES-256"],
    links: [
      { tipo: "codigo", url: "https://github.com/cathsatile/NODUS-Projeto-Integrador-II" },
      { tipo: "documentacao", url: "https://github.com/Davi-KL/NODUS-Projeto-Integrador-II" },
    ],
  },
  {
    id: "forunb",
    tags: ["Django", "Python", "Docker", "GitHub Actions"],
    links: [{ tipo: "codigo", url: "https://github.com/Davi-KL/2024-1-forUnB" }],
  },
  {
    id: "soma",
    tags: ["Python", "Pandas", "Matplotlib", "HTML/CSS/JS"],
    links: [{ tipo: "codigo", url: "https://github.com/cathsatile/SOMA_Social-Media-Overuse-And-Mental-Assessment_" }],
  },
  {
    id: "anp",
    tags: ["Python", "Pandas", "GitHub Actions", "Vue 3", "Plotly"],
    links: [
      { tipo: "analise", url: "/dados-combustiveis", interno: true },
      { tipo: "codigo", url: "https://github.com/Davi-KL/Davi-KL.github.io/tree/main/pipeline" },
    ],
  },
  {
    id: "flowpad",
    tags: ["Python", "pytest", "PyInstaller"],
    links: [{ tipo: "codigo", url: "https://github.com/Davi-KL/FlowPad" }],
  },
  {
    id: "compiladores",
    tags: ["C99", "Makefile", "Análise léxica"],
    links: [{ tipo: "codigo", url: "https://github.com/Davi-KL/Projeto-Compiladores" }],
  },
]
```

- [ ] **Passo 5: Criar `src/content/pt.json`**

```json
{
  "ui": {
    "nav": {
      "rotulo": "Navegação principal",
      "sobre": "Sobre",
      "experiencia": "Experiência",
      "projetos": "Projetos",
      "dados": "Análise de dados",
      "contato": "Contato",
      "menu": "Menu",
      "pularConteudo": "Pular para o conteúdo",
      "idiomaCurto": "EN",
      "idiomaRotulo": "Mudar o idioma para inglês"
    },
    "hero": {
      "statAnos": "anos em health tech",
      "statProjetos": "projetos em destaque",
      "statGasolina": "gasolina no DF hoje (ANP)",
      "verProjetos": "Ver projetos",
      "baixarCv": "Baixar CV"
    },
    "projetos": {
      "papel": "Meu papel",
      "verTodos": "Ver todos os repositórios no GitHub",
      "links": {
        "codigo": "Código",
        "documentacao": "Documentação",
        "analise": "Ver análise"
      }
    },
    "previa": {
      "insightDf": "No DF, a gasolina custa {preco}: {pct} em relação à média nacional.",
      "insightEtanol": "O etanol compensa em {n} dos 27 estados pela regra dos 70%.",
      "insightAlta": "Maior alta em 12 meses: {produto} em {uf} ({pct}).",
      "verAnalise": "Ver análise completa",
      "graficoRotulo": "Preço médio mensal da gasolina nos últimos meses: Brasil e DF",
      "brasil": "Brasil",
      "df": "DF"
    },
    "contato": {
      "email": "E-mail",
      "cv": "Baixar CV (PDF)"
    },
    "produtos": {
      "gasolina": "gasolina",
      "etanol": "etanol",
      "diesel_s10": "diesel S10"
    },
    "dados": {
      "voltar": "Voltar ao portfólio",
      "carregando": "Carregando dados…",
      "indisponivel": "Dados indisponíveis no momento.",
      "verNoGithub": "Ver o projeto no GitHub",
      "dadosAte": "Dados até a semana de {data}.",
      "desatualizado": "Última atualização: dados de {data}",
      "produto": "Combustível",
      "estado": "Estado",
      "modoRotulo": "Tipo de valor",
      "nominal": "Valores nominais",
      "real": "Corrigido pela inflação",
      "brasil": "Brasil",
      "mes": "Mês",
      "preco": "Preço médio",
      "variacao": "Variação em 12 meses",
      "coletas": "Coletas",
      "razao": "Etanol ÷ gasolina",
      "compensa": "Compensa",
      "compensaEtanol": "Compensa etanol",
      "compensaGasolina": "Compensa gasolina",
      "verTabela": "Ver dados em tabela",
      "ocultarTabela": "Ocultar tabela",
      "fontes": "Fontes",
      "verCodigo": "Ver o código do pipeline no GitHub",
      "totalColetas": "{n} preços coletados processados.",
      "ipcaCache": "A série do IPCA não pôde ser atualizada; valores corrigidos até {mes}.",
      "insightEvolucao": "Corrigida pela inflação (em reais de {ref}), a gasolina no Brasil custava {inicial} em {mes} e custa {atual} hoje: {pct}.",
      "insightRanking": "Preço mais alto: {caro} ({precoCaro}). Mais baixo: {barato} ({precoBarato}). O DF é o {pos}º mais caro entre {total} estados.",
      "insightEtanol": "O etanol compensa em {n} estados: {lista}.",
      "insightEtanolNenhum": "Hoje o etanol não compensa em nenhum estado.",
      "graficoEvolucao": "Gráfico de linhas: preço médio mensal de {produto} no Brasil e em {uf}",
      "graficoRanking": "Gráfico de barras: preço médio de {produto} por estado nas últimas quatro semanas",
      "graficoRazao": "Gráfico de barras: razão entre os preços do etanol e da gasolina por estado",
      "graficoRazaoHist": "Gráfico de linhas: razão etanol/gasolina ao longo do tempo no Brasil e em {uf}"
    },
    "meta": {
      "tituloHome": "Davi Levy — Desenvolvedor Full Stack · Dados",
      "descricaoHome": "Portfólio de Davi Levy: desenvolvimento full stack (C#/.NET, Vue, TypeScript) e análise de dados.",
      "tituloDados": "Preços dos combustíveis no Brasil — Davi Levy",
      "descricaoDados": "Análise interativa dos preços de gasolina, etanol e diesel desde 2004, com dados da ANP atualizados toda semana."
    },
    "rodape": {
      "texto": "Feito com Vue 3, Vite e dados abertos da ANP.",
      "codigo": "Código-fonte"
    }
  },
  "conteudo": {
    "hero": {
      "titulo": "Desenvolvedor Full Stack · Dados",
      "frase1": "Código que resolve.",
      "frase2": "Dados que explicam.",
      "resumo": "Dois anos construindo sistemas em ambiente hospitalar de alta demanda na Rede SARAH. Hoje uno desenvolvimento web e análise de dados para transformar necessidades reais em soluções."
    },
    "sobre": {
      "titulo": "Sobre",
      "paragrafos": [
        "Sou desenvolvedor full stack júnior, com dois anos de experiência na Rede SARAH de Hospitais de Reabilitação, em Brasília. Comecei no suporte de TI e evoluí para o desenvolvimento de sistemas web: consultas e manutenção em PL/SQL (Oracle) em produção, páginas e dashboards internos e a modernização de sistemas legados — sempre em contato direto com equipes clínicas e administrativas.",
        "Curso Ciência da Computação no UniCEUB e aprofundo minha formação em Ciência de Dados e Inteligência Artificial. Busco oportunidades 100% remotas em desenvolvimento web, back-end, full stack ou análise de dados."
      ],
      "stackTitulo": "Stack",
      "grupos": {
        "front": "Front-end",
        "back": "Back-end",
        "dados": "Dados/IA",
        "devops": "DevOps"
      },
      "formacaoTitulo": "Formação",
      "formacao": [
        { "instituicao": "UniCEUB — Centro Universitário de Brasília", "curso": "Ciência da Computação", "periodo": "2025 – 2027" },
        { "instituicao": "Universidade de Brasília (UnB)", "curso": "Engenharia de Software", "periodo": "2022 – 2024" },
        { "instituicao": "Faculdade BookPlay", "curso": "Fundamentos de Ciência de Dados (em andamento)", "periodo": "" }
      ],
      "certificacoesTitulo": "Certificações",
      "certificacoes": ["Google AI Essentials", "Google AI Professional Certificate"],
      "idiomasTitulo": "Idiomas",
      "idiomas": ["Português — nativo", "Inglês — fluente"]
    },
    "experiencia": {
      "titulo": "Experiência",
      "destaque": {
        "empresa": "Rede SARAH de Hospitais de Reabilitação (Associação das Pioneiras Sociais)",
        "cargo": "Estagiário de TI — Desenvolvedor de Sistemas Web",
        "periodo": "jan/2024 – jan/2026",
        "local": "Brasília, DF",
        "itens": [
          "PL/SQL (Oracle) em larga escala: consultas, manutenção e análise de dados em um banco hospitalar de grande volume, com dados sensíveis de pacientes protegidos pela LGPD.",
          "Desenvolvimento web interno: páginas e dashboards para controle de dados e de acesso de colaboradores na intranet, com Vue.js, Quasar, C# e ASP.NET MVC/.NET Framework.",
          "Modernização de sistema legado: participação na migração de uma aplicação desktop para a web com Vue.js, Quasar e C#.",
          "Testes de software: desenvolvimento e execução de testes para garantia de qualidade.",
          "Suporte e infraestrutura: dezenas de chamados por mês, configuração de máquinas e impressoras e suporte aos colaboradores."
        ]
      },
      "outrasTitulo": "Outras experiências",
      "outras": [
        { "empresa": "Zenit Aerospace", "cargo": "Assessor Comercial", "periodo": "2023 – 2024" },
        { "empresa": "Sabin Medicina Diagnóstica", "cargo": "Jovem Aprendiz", "periodo": "2021 – 2022" }
      ]
    },
    "projetos": {
      "titulo": "Projetos",
      "subtitulo": "Projetos em equipe e individuais — cada card diz qual foi o meu papel.",
      "itens": {
        "nodus": {
          "titulo": "NODUS",
          "descricao": "Aplicativo desktop para Windows que permite a psicólogos clínicos registrar prontuários, agendar sessões e acompanhar o histórico de pacientes. Funciona 100% offline: Angular, Express local e SQLite empacotados com Electron, com dados cifrados em AES-256 e chave derivada da senha, mantida só em memória — em conformidade com a LGPD e a Resolução CFP 06/2019. Projeto Integrador II do CEUB, com Catharina e Miguel.",
          "papel": "Gerente de projeto, Scrum Master, desenvolvimento back-end e DevOps."
        },
        "forunb": {
          "titulo": "ForUnB",
          "descricao": "Plataforma open-source de perguntas e respostas para mentoria entre estudantes da UnB, com pipeline de CI/CD.",
          "papel": "Back-end, testes e DevOps: automação de CI/CD e deploy."
        },
        "soma": {
          "titulo": "SOMA",
          "descricao": "Plataforma de análise do uso excessivo de redes sociais e de seus efeitos na saúde mental, com dashboard interativo.",
          "papel": "Front-end, criação dos gráficos e análise dos dados coletados pela Catharina."
        },
        "anp": {
          "titulo": "Análise de Preços de Combustíveis (ANP)",
          "descricao": "Pipeline em Python que coleta, limpa e agrega a série histórica de preços de combustíveis da ANP desde 2004, com atualização semanal automática via GitHub Actions e dashboard interativo.",
          "papel": "Projeto individual: coleta, tratamento, análise, visualização e automação."
        },
        "flowpad": {
          "titulo": "FlowPad",
          "descricao": "Aplicativo em segundo plano para capturar ideias sem interromper o trabalho: um atalho (Ctrl+Shift+Space) abre a janela e o registro leva menos de 3 segundos. Tem cinco tipos de entrada, lembretes automáticos, dashboard com busca e armazenamento local em JSON.",
          "papel": "Projeto individual."
        },
        "compiladores": {
          "titulo": "Analisador Léxico Portugol",
          "descricao": "Analisador léxico em C99 para uma linguagem no estilo Portugol, desenvolvido para a disciplina de Compiladores do CEUB. Reconhece os tokens da linguagem, trata palavras reservadas, monta a tabela de símbolos e entrega um token por vez ao parser, com build via Makefile e testes automatizados.",
          "papel": "Projeto individual."
        }
      }
    },
    "previa": {
      "titulo": "Análise de dados: preços dos combustíveis",
      "subtitulo": "Um pipeline próprio coleta os dados abertos da ANP toda semana. Alguns números de agora:"
    },
    "contato": {
      "titulo": "Contato",
      "texto": "Estou aberto a oportunidades 100% remotas. O jeito mais rápido de falar comigo é por e-mail ou LinkedIn."
    },
    "dados": {
      "titulo": "Quanto custa abastecer no Brasil?",
      "intro": "Análise dos preços de gasolina, etanol e diesel S10 com base na Série Histórica de Preços de Combustíveis da ANP, de 2004 até hoje. Os dados são coletados, limpos e agregados por um pipeline em Python e atualizados automaticamente toda semana.",
      "evolucao": {
        "titulo": "1. Como os preços mudaram ao longo do tempo",
        "explicacao": "Média mensal do preço de venda ao consumidor. Com a correção pelo IPCA, todos os valores ficam em reais do mês de referência — assim dá para comparar 2004 com hoje de forma justa."
      },
      "ranking": {
        "titulo": "2. Onde o combustível é mais caro",
        "explicacao": "Preço médio nas últimas quatro semanas por estado, do mais caro para o mais barato. Passe o mouse ou toque nas barras para ver a variação em 12 meses. A linha tracejada é a média nacional."
      },
      "etanol": {
        "titulo": "3. Etanol ou gasolina?",
        "explicacao": "Como o etanol rende cerca de 70% da gasolina, ele compensa quando custa menos de 70% do preço dela. As barras mostram essa razão por estado; à esquerda da linha tracejada, vale abastecer com etanol.",
        "historicoTitulo": "A razão ao longo do tempo"
      },
      "metodologia": {
        "titulo": "Metodologia",
        "itens": [
          "Fontes: Série Histórica de Preços de Combustíveis da ANP (levantamento semanal em postos de todo o país) e IPCA mensal do Banco Central (série SGS 433).",
          "Limpeza: padronização de produtos, estados, datas e preços; remoção de registros duplicados do mesmo posto e de preços fora da faixa de R$ 0,50 a R$ 20,00 por litro.",
          "Médias: calculadas sobre todas as coletas do período. A média nacional usa todas as coletas do país, não a média das médias estaduais.",
          "Diesel S10: a série começa em 2013, quando o produto passou a ser pesquisado. O diesel comum não entra na análise para não misturar produtos diferentes.",
          "Inflação: os valores corrigidos usam o IPCA acumulado até o mês de referência. Meses posteriores ao último IPCA publicado ficam com o valor nominal.",
          "Atualização: um GitHub Actions roda o pipeline todo sábado; se alguma validação falhar, nada é publicado e o site mantém a última versão válida."
        ]
      }
    }
  }
}
```

- [ ] **Passo 6: Criar `src/content/en.json`**

```json
{
  "ui": {
    "nav": {
      "rotulo": "Main navigation",
      "sobre": "About",
      "experiencia": "Experience",
      "projetos": "Projects",
      "dados": "Data analysis",
      "contato": "Contact",
      "menu": "Menu",
      "pularConteudo": "Skip to content",
      "idiomaCurto": "PT",
      "idiomaRotulo": "Switch language to Portuguese"
    },
    "hero": {
      "statAnos": "years in health tech",
      "statProjetos": "featured projects",
      "statGasolina": "gasoline in Brasília today (ANP)",
      "verProjetos": "See projects",
      "baixarCv": "Download CV"
    },
    "projetos": {
      "papel": "My role",
      "verTodos": "See all repositories on GitHub",
      "links": {
        "codigo": "Code",
        "documentacao": "Documentation",
        "analise": "See analysis"
      }
    },
    "previa": {
      "insightDf": "In Brasília (DF), gasoline costs {preco}: {pct} compared with the national average.",
      "insightEtanol": "Ethanol pays off in {n} of the 27 states under the 70% rule.",
      "insightAlta": "Biggest 12-month increase: {produto} in {uf} ({pct}).",
      "verAnalise": "See full analysis",
      "graficoRotulo": "Monthly average gasoline price in recent months: Brazil and Brasília (DF)",
      "brasil": "Brazil",
      "df": "DF"
    },
    "contato": {
      "email": "Email",
      "cv": "Download CV (PDF)"
    },
    "produtos": {
      "gasolina": "gasoline",
      "etanol": "ethanol",
      "diesel_s10": "S10 diesel"
    },
    "dados": {
      "voltar": "Back to portfolio",
      "carregando": "Loading data…",
      "indisponivel": "Data unavailable right now.",
      "verNoGithub": "See the project on GitHub",
      "dadosAte": "Data up to the week of {data}.",
      "desatualizado": "Last update: data from {data}",
      "produto": "Fuel",
      "estado": "State",
      "modoRotulo": "Value type",
      "nominal": "Nominal values",
      "real": "Inflation-adjusted",
      "brasil": "Brazil",
      "mes": "Month",
      "preco": "Average price",
      "variacao": "12-month change",
      "coletas": "Samples",
      "razao": "Ethanol ÷ gasoline",
      "compensa": "Better deal",
      "compensaEtanol": "Ethanol pays off",
      "compensaGasolina": "Gasoline pays off",
      "verTabela": "Show data table",
      "ocultarTabela": "Hide table",
      "fontes": "Sources",
      "verCodigo": "See the pipeline code on GitHub",
      "totalColetas": "{n} collected prices processed.",
      "ipcaCache": "The IPCA series could not be updated; values adjusted up to {mes}.",
      "insightEvolucao": "Adjusted for inflation (in reais of {ref}), gasoline in Brazil cost {inicial} in {mes} and costs {atual} today: {pct}.",
      "insightRanking": "Highest price: {caro} ({precoCaro}). Lowest: {barato} ({precoBarato}). Brasília (DF) ranks #{pos} most expensive out of {total} states.",
      "insightEtanol": "Ethanol pays off in {n} states: {lista}.",
      "insightEtanolNenhum": "Right now ethanol doesn't pay off in any state.",
      "graficoEvolucao": "Line chart: monthly average {produto} price in Brazil and {uf}",
      "graficoRanking": "Bar chart: average {produto} price by state over the last four weeks",
      "graficoRazao": "Bar chart: ethanol-to-gasoline price ratio by state",
      "graficoRazaoHist": "Line chart: ethanol-to-gasoline ratio over time in Brazil and {uf}"
    },
    "meta": {
      "tituloHome": "Davi Levy — Full Stack Developer · Data",
      "descricaoHome": "Davi Levy's portfolio: full stack development (C#/.NET, Vue, TypeScript) and data analysis.",
      "tituloDados": "Fuel prices in Brazil — Davi Levy",
      "descricaoDados": "Interactive analysis of gasoline, ethanol and diesel prices since 2004, with ANP data updated every week."
    },
    "rodape": {
      "texto": "Built with Vue 3, Vite and open data from ANP.",
      "codigo": "Source code"
    }
  },
  "conteudo": {
    "hero": {
      "titulo": "Full Stack Developer · Data",
      "frase1": "Code that solves.",
      "frase2": "Data that explains.",
      "resumo": "Two years building systems in a high-demand hospital environment at Rede SARAH. Today I combine web development and data analysis to turn real needs into working solutions."
    },
    "sobre": {
      "titulo": "About",
      "paragrafos": [
        "I'm a junior full stack developer with two years of experience at Rede SARAH, a network of rehabilitation hospitals in Brasília, Brazil. I started in IT support and grew into web systems development: PL/SQL (Oracle) queries and maintenance in production, internal pages and dashboards, and legacy system modernization — always working directly with clinical and administrative teams.",
        "I'm studying Computer Science at UniCEUB and deepening my knowledge of Data Science and Artificial Intelligence. I'm looking for 100% remote opportunities in web, back-end, full stack or data analysis roles."
      ],
      "stackTitulo": "Stack",
      "grupos": {
        "front": "Front-end",
        "back": "Back-end",
        "dados": "Data/AI",
        "devops": "DevOps"
      },
      "formacaoTitulo": "Education",
      "formacao": [
        { "instituicao": "UniCEUB — Centro Universitário de Brasília", "curso": "B.Sc. in Computer Science", "periodo": "2025 – 2027" },
        { "instituicao": "University of Brasília (UnB)", "curso": "Software Engineering", "periodo": "2022 – 2024" },
        { "instituicao": "Faculdade BookPlay", "curso": "Data Science Fundamentals (in progress)", "periodo": "" }
      ],
      "certificacoesTitulo": "Certifications",
      "certificacoes": ["Google AI Essentials", "Google AI Professional Certificate"],
      "idiomasTitulo": "Languages",
      "idiomas": ["Portuguese — native", "English — full professional proficiency"]
    },
    "experiencia": {
      "titulo": "Experience",
      "destaque": {
        "empresa": "Rede SARAH Rehabilitation Hospitals (Associação das Pioneiras Sociais)",
        "cargo": "IT Intern — Web Systems Developer",
        "periodo": "Jan 2024 – Jan 2026",
        "local": "Brasília, Brazil",
        "itens": [
          "Large-scale PL/SQL (Oracle): queries, maintenance and data analysis on a high-volume hospital database with sensitive patient data protected under Brazil's LGPD.",
          "Internal web development: pages and dashboards for data control and staff access on the intranet, using Vue.js, Quasar, C# and ASP.NET MVC/.NET Framework.",
          "Legacy modernization: took part in migrating a desktop application to the web with Vue.js, Quasar and C#.",
          "Software testing: writing and running tests for quality assurance.",
          "Support and infrastructure: dozens of tickets per month, machine and printer setup, and staff support."
        ]
      },
      "outrasTitulo": "Other experience",
      "outras": [
        { "empresa": "Zenit Aerospace", "cargo": "Sales Associate", "periodo": "2023 – 2024" },
        { "empresa": "Sabin Medicina Diagnóstica", "cargo": "Young Apprentice", "periodo": "2021 – 2022" }
      ]
    },
    "projetos": {
      "titulo": "Projects",
      "subtitulo": "Team and solo projects — each card says what my role was.",
      "itens": {
        "nodus": {
          "titulo": "NODUS",
          "descricao": "Windows desktop app that lets clinical psychologists keep patient records, schedule sessions and track patient history. Works 100% offline: Angular, a local Express server and SQLite packaged with Electron, with data encrypted using AES-256 and a key derived from the user's password that only lives in memory — compliant with Brazil's LGPD and CFP Resolution 06/2019. Capstone project (Projeto Integrador II) at CEUB, with Catharina and Miguel.",
          "papel": "Project manager, Scrum Master, back-end development and DevOps."
        },
        "forunb": {
          "titulo": "ForUnB",
          "descricao": "Open-source Q&A platform for peer mentoring among University of Brasília students, with a CI/CD pipeline.",
          "papel": "Back-end, testing and DevOps: CI/CD automation and deployment."
        },
        "soma": {
          "titulo": "SOMA",
          "descricao": "Platform that analyzes social media overuse and its effects on mental health, with an interactive dashboard.",
          "papel": "Front-end, chart design and analysis of the data collected by Catharina."
        },
        "anp": {
          "titulo": "Fuel Price Analysis (ANP)",
          "descricao": "Python pipeline that collects, cleans and aggregates Brazil's official fuel price survey (ANP) since 2004, with automatic weekly updates through GitHub Actions and an interactive dashboard.",
          "papel": "Solo project: collection, processing, analysis, visualization and automation."
        },
        "flowpad": {
          "titulo": "FlowPad",
          "descricao": "Background app to capture ideas without breaking your flow: a shortcut (Ctrl+Shift+Space) opens a popup and saving takes under 3 seconds. Five entry types, automatic reminders, a searchable dashboard and local JSON storage.",
          "papel": "Solo project."
        },
        "compiladores": {
          "titulo": "Portugol Lexical Analyzer",
          "descricao": "Lexical analyzer in C99 for a Portugol-style language, built for the Compilers course at CEUB. It recognizes the language's tokens, handles reserved words, builds the symbol table and hands one token at a time to the parser, with a Makefile build and automated tests.",
          "papel": "Solo project."
        }
      }
    },
    "previa": {
      "titulo": "Data analysis: fuel prices in Brazil",
      "subtitulo": "My own pipeline collects Brazil's open fuel price data (ANP) every week. A few numbers right now:"
    },
    "contato": {
      "titulo": "Contact",
      "texto": "I'm open to 100% remote opportunities. The fastest way to reach me is by email or LinkedIn."
    },
    "dados": {
      "titulo": "How much does it cost to fill up in Brazil?",
      "intro": "Analysis of gasoline, ethanol and S10 diesel prices based on the ANP Fuel Price Historical Series, from 2004 to today. The data is collected, cleaned and aggregated by a Python pipeline and updated automatically every week.",
      "evolucao": {
        "titulo": "1. How prices changed over time",
        "explicacao": "Monthly average retail price. With the IPCA inflation adjustment, all values are expressed in reais of the reference month — so 2004 can be fairly compared with today."
      },
      "ranking": {
        "titulo": "2. Where fuel is most expensive",
        "explicacao": "Average price over the last four weeks by state, from most to least expensive. Hover over or tap a bar to see the 12-month change. The dashed line is the national average."
      },
      "etanol": {
        "titulo": "3. Ethanol or gasoline?",
        "explicacao": "Ethanol delivers roughly 70% of gasoline's mileage, so it pays off when it costs less than 70% of the gasoline price. The bars show that ratio by state; left of the dashed line, ethanol is the better deal.",
        "historicoTitulo": "The ratio over time"
      },
      "metodologia": {
        "titulo": "Methodology",
        "itens": [
          "Sources: ANP Fuel Price Historical Series (weekly survey at gas stations nationwide) and monthly IPCA inflation from Brazil's Central Bank (SGS series 433).",
          "Cleaning: products, states, dates and prices are standardized; duplicate records from the same station and prices outside the R$ 0.50 to R$ 20.00 per liter range are removed.",
          "Averages: computed over every price collected in the period. The national average uses all collections in the country, not the average of state averages.",
          "S10 diesel: the series starts in 2013, when the product began to be surveyed. Regular diesel is left out so different products are not mixed.",
          "Inflation: adjusted values use the IPCA accumulated up to the reference month. Months after the latest published IPCA keep their nominal value.",
          "Updates: a GitHub Actions workflow runs the pipeline every Saturday; if any validation fails, nothing is published and the site keeps the last valid version."
        ]
      }
    }
  }
}
```

- [ ] **Passo 7: Criar `useConteudo` e trocar o tipo em `format.ts`**

`site/src/composables/useConteudo.ts`:

```ts
import { computed, type ComputedRef } from "vue"
import { useI18n } from "vue-i18n"
import en from "../content/en.json"
import pt from "../content/pt.json"

export type Conteudo = typeof pt.conteudo

const POR_IDIOMA: Record<string, Conteudo> = { pt: pt.conteudo, en: en.conteudo }

export function useConteudo(): ComputedRef<Conteudo> {
  const { locale } = useI18n()
  return computed(() => POR_IDIOMA[locale.value] ?? pt.conteudo)
}
```

Em `site/src/lib/format.ts`, trocar a primeira linha `type Idioma = "pt" | "en"` por:

```ts
import type { Idioma } from "../i18n"
```

- [ ] **Passo 8: Rodar e ver passar**

Rodar: `cd site && npx vitest run tests/i18n.spec.ts tests/format.spec.ts`
Esperado: 12 passed.

- [ ] **Passo 9: Commit**

```bash
cd site
git add src/i18n.ts src/content src/composables/useConteudo.ts src/lib/format.ts tests/i18n.spec.ts
git commit -m "feat(site): conteúdo bilíngue, perfil e i18n" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 3: Tipos de dados, fixtures, contrato e carregamento

**Arquivos:**
- Criar: `site/src/types/dados.ts`
- Criar: `site/src/__fixtures__/meta.json`, `evolucao.json`, `ranking_uf.json`, `etanol_gasolina.json`
- Criar: `site/src/composables/useFuelData.ts`
- Criar: `site/src/lib/stale.ts`
- Criar: `site/tests/contrato.spec.ts`, `site/tests/useFuelData.spec.ts`, `site/tests/stale.spec.ts`
- Criar: `site/tests/montar.ts` (helpers de teste para as tarefas seguintes)

**Interfaces:**
- Produz:
  - `src/types/dados.ts`: `Produto`, `SerieProduto`, `Evolucao`, `ItemRanking`, `Ranking`, `ItemRazao`, `EtanolGasolina` e `Meta`, espelhando `schemas/`.
  - `src/composables/useFuelData.ts`:
    - `type ArquivoDados`;
    - `carregarJson<T>(arquivo): Promise<T>`, com cache por URL; um erro remove a entrada do cache;
    - `useFuelData<T>(arquivo): { dados: Ref<T | null>; erro: Ref<boolean>; carregando: Ref<boolean> }`;
    - `limparCacheDados(): void`.
  - `src/lib/stale.ts`: `diasDesde(iso, agora: Date): number` e `dadosDesatualizados(semana: string, agora: Date, limiteDias = 21): boolean`.
  - `tests/montar.ts`:
    - `montar(componente, { props?, rota?, idioma? }): Promise<VueWrapper>`;
    - `simularDados(respostas: Record<string, unknown | number>)`, onde um número responde com esse status HTTP e a ausência da chave responde 404;
    - `texto(wrapper): string`, que normaliza os espaços.

- [ ] **Passo 1: Criar os tipos**

`site/src/types/dados.ts`:

```ts
export type Produto = "gasolina" | "etanol" | "diesel_s10"
export type Serie = (number | null)[]

export interface SerieProduto {
  nominal: Serie
  real: Serie
}

export interface Evolucao {
  meses: string[]
  ipca_ref: string
  series: Record<string, Partial<Record<Produto, SerieProduto>>>
}

export interface ItemRanking {
  uf: string
  produto: Produto
  preco_medio: number
  variacao_12m_pct: number | null
  n_coletas: number
}

export interface Ranking {
  periodo: { inicio: string; fim: string }
  itens: ItemRanking[]
}

export interface ItemRazao {
  uf: string
  razao: number
  compensa: "etanol" | "gasolina"
}

export interface EtanolGasolina {
  limiar: number
  atual: ItemRazao[]
  historico: { meses: string[]; razao: Record<string, Serie> }
}

export interface Meta {
  atualizado_em: string
  semana_mais_recente: string
  n_coletas_total: number
  ipca_ate: string
  ipca_em_cache: boolean
  fontes: { nome: string; url: string }[]
  destaques: {
    gasolina_df: number
    gasolina_br: number
    diff_df_br_pct: number | null
    ufs_etanol_compensa: number
    maior_alta_12m: { uf: string; produto: Produto; pct: number } | null
  }
  serie_home: { meses: string[]; gasolina_br: Serie; gasolina_df: Serie }
}
```

- [ ] **Passo 2: Criar os fixtures**

Os valores de setembro de 2026 vêm do teste real do pipeline.

`site/src/__fixtures__/meta.json`:

```json
{
  "atualizado_em": "2026-09-26T12:04:00Z",
  "semana_mais_recente": "2026-09-21",
  "n_coletas_total": 420419,
  "ipca_ate": "2026-08",
  "ipca_em_cache": false,
  "fontes": [
    { "nome": "ANP — Série Histórica de Preços de Combustíveis", "url": "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis" },
    { "nome": "Banco Central — SGS 433 (IPCA)", "url": "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json" }
  ],
  "destaques": {
    "gasolina_df": 6.669,
    "gasolina_br": 6.558,
    "diff_df_br_pct": 1.7,
    "ufs_etanol_compensa": 11,
    "maior_alta_12m": { "uf": "AC", "produto": "diesel_s10", "pct": 8.1 }
  },
  "serie_home": {
    "meses": ["2026-06", "2026-07", "2026-08", "2026-09"],
    "gasolina_br": [6.41, 6.47, 6.52, 6.558],
    "gasolina_df": [6.5, 6.55, null, 6.669]
  }
}
```

`site/src/__fixtures__/evolucao.json`:

```json
{
  "meses": ["2026-06", "2026-07", "2026-08", "2026-09"],
  "ipca_ref": "2026-08",
  "series": {
    "BR": {
      "gasolina": { "nominal": [6.41, 6.47, 6.52, 6.558], "real": [6.43, 6.48, 6.52, 6.558] },
      "etanol": { "nominal": [4.2, 4.25, 4.28, 4.3], "real": [4.21, 4.26, 4.28, 4.3] },
      "diesel_s10": { "nominal": [6.8, 6.85, 6.88, 6.9], "real": [6.82, 6.86, 6.88, 6.9] }
    },
    "DF": {
      "gasolina": { "nominal": [6.5, 6.55, 6.61, 6.669], "real": [6.52, 6.56, 6.61, 6.669] },
      "etanol": { "nominal": [4.3, 4.33, 4.36, 4.38], "real": [4.31, 4.34, 4.36, 4.38] },
      "diesel_s10": { "nominal": [null, 6.9, 6.93, 6.95], "real": [null, 6.91, 6.93, 6.95] }
    },
    "SP": {
      "gasolina": { "nominal": [6.2, 6.24, 6.27, 6.3], "real": [6.22, 6.25, 6.27, 6.3] },
      "etanol": { "nominal": [3.7, 3.72, 3.73, 3.74], "real": [3.71, 3.73, 3.73, 3.74] },
      "diesel_s10": { "nominal": [6.6, 6.65, 6.68, 6.7], "real": [6.62, 6.66, 6.68, 6.7] }
    }
  }
}
```

`site/src/__fixtures__/ranking_uf.json`:

```json
{
  "periodo": { "inicio": "2026-08-31", "fim": "2026-09-25" },
  "itens": [
    { "uf": "BR", "produto": "gasolina", "preco_medio": 6.558, "variacao_12m_pct": 3.2, "n_coletas": 90000 },
    { "uf": "BR", "produto": "etanol", "preco_medio": 4.3, "variacao_12m_pct": 1.1, "n_coletas": 80000 },
    { "uf": "BR", "produto": "diesel_s10", "preco_medio": 6.9, "variacao_12m_pct": 4.0, "n_coletas": 60000 },
    { "uf": "AC", "produto": "gasolina", "preco_medio": 7.45, "variacao_12m_pct": 5.0, "n_coletas": 300 },
    { "uf": "AC", "produto": "etanol", "preco_medio": 5.4, "variacao_12m_pct": 2.0, "n_coletas": 200 },
    { "uf": "AC", "produto": "diesel_s10", "preco_medio": 7.9, "variacao_12m_pct": 8.1, "n_coletas": 250 },
    { "uf": "DF", "produto": "gasolina", "preco_medio": 6.669, "variacao_12m_pct": 2.9, "n_coletas": 1200 },
    { "uf": "DF", "produto": "etanol", "preco_medio": 4.38, "variacao_12m_pct": null, "n_coletas": 1100 },
    { "uf": "DF", "produto": "diesel_s10", "preco_medio": 6.95, "variacao_12m_pct": 3.5, "n_coletas": 900 },
    { "uf": "SP", "produto": "gasolina", "preco_medio": 6.3, "variacao_12m_pct": 2.0, "n_coletas": 15000 },
    { "uf": "SP", "produto": "etanol", "preco_medio": 3.74, "variacao_12m_pct": 0.5, "n_coletas": 14000 },
    { "uf": "SP", "produto": "diesel_s10", "preco_medio": 6.7, "variacao_12m_pct": 3.8, "n_coletas": 9000 }
  ]
}
```

`site/src/__fixtures__/etanol_gasolina.json`:

```json
{
  "limiar": 0.7,
  "atual": [
    { "uf": "BR", "razao": 0.656, "compensa": "etanol" },
    { "uf": "AC", "razao": 0.725, "compensa": "gasolina" },
    { "uf": "DF", "razao": 0.657, "compensa": "etanol" },
    { "uf": "SP", "razao": 0.594, "compensa": "etanol" }
  ],
  "historico": {
    "meses": ["2026-06", "2026-07", "2026-08", "2026-09"],
    "razao": {
      "BR": [0.655, 0.657, 0.656, 0.656],
      "AC": [0.73, 0.728, 0.726, 0.725],
      "DF": [0.662, 0.661, null, 0.657],
      "SP": [0.597, 0.596, 0.595, 0.594]
    }
  }
}
```

- [ ] **Passo 3: Escrever os testes que falham**

`site/tests/contrato.spec.ts`:

```ts
import Ajv2020 from "ajv/dist/2020"
import { existsSync, readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

// Caminhos pelo Node (e não `new URL(..., import.meta.url)`, que o Vite trata como asset e bloqueia fora de site/).
const SITE = join(dirname(fileURLToPath(import.meta.url)), "..")
const ARQUIVOS = ["meta", "evolucao", "ranking_uf", "etanol_gasolina"] as const
const ler = (caminho: string) => JSON.parse(readFileSync(caminho, "utf8"))
const schema = (nome: string) => ler(join(SITE, "..", "schemas", `${nome}.schema.json`))

function validar(nome: string, dados: unknown): string | null {
  const ajv = new Ajv2020({ allErrors: true, strict: false })
  const ok = ajv.validate(schema(nome), dados)
  return ok ? null : JSON.stringify(ajv.errors)
}

describe("contrato com o pipeline (schemas/)", () => {
  it.each(ARQUIVOS)("fixture %s.json segue o schema", (nome) => {
    expect(validar(nome, ler(join(SITE, "src", "__fixtures__", `${nome}.json`)))).toBeNull()
  })

  it.each(ARQUIVOS)("dado publicado %s.json (se existir) segue o schema", (nome) => {
    const publicado = join(SITE, "public", "data", `${nome}.json`)
    if (!existsSync(publicado)) return
    expect(validar(nome, ler(publicado))).toBeNull()
  })
})
```

`site/tests/stale.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import { dadosDesatualizados, diasDesde } from "../src/lib/stale"

describe("dados desatualizados", () => {
  const agora = new Date("2026-09-30T12:00:00Z")
  it("conta dias desde a data", () => {
    expect(diasDesde("2026-09-21", agora)).toBe(9)
  })
  it("até 21 dias está em dia", () => {
    expect(dadosDesatualizados("2026-09-09", agora)).toBe(false)
  })
  it("mais de 21 dias está desatualizado", () => {
    expect(dadosDesatualizados("2026-09-08", agora)).toBe(true)
  })
})
```

`site/tests/useFuelData.spec.ts`:

```ts
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
```

`site/tests/montar.ts`:

```ts
import { flushPromises, mount, type VueWrapper } from "@vue/test-utils"
import { vi } from "vitest"
import type { Component } from "vue"
import { createMemoryHistory } from "vue-router"
import { limparCacheDados } from "../src/composables/useFuelData"
import { i18n, type Idioma } from "../src/i18n"
import { criarRouter } from "../src/router"

/** Simula o fetch dos JSONs. Número = status HTTP de erro; "rede" = falha de rede; chave ausente = 404. */
export function simularDados(respostas: Record<string, unknown>) {
  limparCacheDados()
  const fetch = vi.fn(async (url: string | URL) => {
    const nome = String(url).split("/").pop() ?? ""
    const resposta = respostas[nome]
    if (resposta === "rede") throw new TypeError("Failed to fetch")
    const status = resposta === undefined ? 404 : typeof resposta === "number" ? resposta : 200
    return { ok: status === 200, status, json: async () => resposta } as Response
  })
  vi.stubGlobal("fetch", fetch)
  return fetch
}

export async function montar(
  componente: Component,
  opcoes: { props?: Record<string, unknown>; slots?: Record<string, () => unknown>; rota?: string; idioma?: Idioma } = {},
): Promise<VueWrapper> {
  i18n.global.locale.value = opcoes.idioma ?? "pt"
  const router = criarRouter(createMemoryHistory())
  await router.push(opcoes.rota ?? "/")
  await router.isReady()
  const wrapper = mount(componente, {
    props: opcoes.props,
    slots: opcoes.slots as never,
    global: { plugins: [i18n, router] },
  })
  await flushPromises()
  await flushPromises()
  return wrapper
}

/** Texto do componente (ou de um elemento dele) com espaços normalizados, inclusive o espaço fixo do "R$ ". */
export const texto = (w: { text(): string }): string => w.text().replace(/\s+/g, " ")
```

O `montar` importa `criarRouter`, que é criado na Tarefa 4. Nesta tarefa só `simularDados` é usado. Por isso, crie já um `src/router.ts` provisório, que a Tarefa 4 substitui:

```ts
import { createRouter, createWebHistory, type RouterHistory } from "vue-router"

export function criarRouter(history: RouterHistory = createWebHistory(import.meta.env.BASE_URL)) {
  return createRouter({ history, routes: [{ path: "/", component: { template: "<div />" } }] })
}
```

- [ ] **Passo 4: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/contrato.spec.ts tests/stale.spec.ts tests/useFuelData.spec.ts`
Esperado: `contrato` passa, porque só lê arquivos. `stale` e `useFuelData` FALHAM com `Failed to resolve import`.

- [ ] **Passo 5: Implementar `stale.ts` e `useFuelData.ts`**

`site/src/lib/stale.ts`:

```ts
const DIA_MS = 86_400_000

export function diasDesde(iso: string, agora: Date): number {
  const [ano, mes, dia] = iso.split("-").map(Number)
  return Math.floor((agora.getTime() - Date.UTC(ano, mes - 1, dia)) / DIA_MS)
}

export function dadosDesatualizados(semanaMaisRecente: string, agora: Date, limiteDias = 21): boolean {
  return diasDesde(semanaMaisRecente, agora) > limiteDias
}
```

`site/src/composables/useFuelData.ts`:

```ts
import { ref, type Ref } from "vue"

export type ArquivoDados = "meta.json" | "evolucao.json" | "ranking_uf.json" | "etanol_gasolina.json"

const cache = new Map<string, Promise<unknown>>()

export function limparCacheDados(): void {
  cache.clear()
}

export function carregarJson<T>(arquivo: ArquivoDados): Promise<T> {
  const url = `${import.meta.env.BASE_URL}data/${arquivo}`
  let promessa = cache.get(url)
  if (!promessa) {
    promessa = fetch(url).then((resposta) => {
      if (!resposta.ok) throw new Error(`HTTP ${resposta.status} ao carregar ${arquivo}`)
      return resposta.json()
    })
    promessa.catch(() => cache.delete(url))
    cache.set(url, promessa)
  }
  return promessa as Promise<T>
}

export interface EstadoDados<T> {
  dados: Ref<T | null>
  erro: Ref<boolean>
  carregando: Ref<boolean>
}

export function useFuelData<T>(arquivo: ArquivoDados): EstadoDados<T> {
  const dados = ref(null) as Ref<T | null>
  const erro = ref(false)
  const carregando = ref(true)
  carregarJson<T>(arquivo)
    .then((valor) => {
      dados.value = valor
    })
    .catch(() => {
      erro.value = true
    })
    .finally(() => {
      carregando.value = false
    })
  return { dados, erro, carregando }
}
```

- [ ] **Passo 6: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam (format, i18n, contrato, stale, useFuelData).

- [ ] **Passo 7: Commit**

```bash
cd site
git add src/types src/__fixtures__ src/composables/useFuelData.ts src/lib/stale.ts src/router.ts tests/contrato.spec.ts tests/stale.spec.ts tests/useFuelData.spec.ts tests/montar.ts
git commit -m "feat(site): tipos, fixtures validados pelo contrato e carregamento de dados" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 4: Rotas, app, cabeçalho, rodapé e SEO

**Arquivos:**
- Modificar (substituir por completo): `site/src/router.ts`
- Criar: `site/src/main.ts`, `site/src/App.vue`
- Criar: `site/src/lib/seo.ts`
- Criar: `site/src/components/layout/SiteHeader.vue`, `site/src/components/layout/SiteFooter.vue`
- Criar: `site/src/views/HomeView.vue` (esqueleto, completado nas Tarefas 5 a 7)
- Criar: `site/src/views/FuelDataView.vue` (esqueleto, completado na Tarefa 10)
- Criar: `site/tests/router.spec.ts`, `site/tests/SiteHeader.spec.ts`

**Interfaces:**
- Consome: `i18n`, `definirIdioma` e `aplicarLang` (Tarefa 2).
- Produz:
  - `criarRouter(history?: RouterHistory): Router`, com as rotas `home` (`/`), `dados` (`/dados-combustiveis`, carregada sob demanda) e o redirecionamento das demais para `/`.
  - `aplicarMeta({ titulo, descricao, idioma }): void`.

- [ ] **Passo 1: Escrever os testes que falham**

`site/tests/router.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import { createMemoryHistory } from "vue-router"
import { criarRouter } from "../src/router"

describe("rotas", () => {
  it("home e página de dados", async () => {
    const router = criarRouter(createMemoryHistory())
    await router.push("/dados-combustiveis")
    expect(router.currentRoute.value.name).toBe("dados")
    await router.push("/")
    expect(router.currentRoute.value.name).toBe("home")
  })

  it("aceita barra final (GitHub Pages serve /dados-combustiveis/)", async () => {
    const router = criarRouter(createMemoryHistory())
    await router.push("/dados-combustiveis/")
    expect(router.currentRoute.value.name).toBe("dados")
  })

  it("rota desconhecida volta para a home", async () => {
    const router = criarRouter(createMemoryHistory())
    await router.push("/nao-existe")
    expect(router.currentRoute.value.path).toBe("/")
  })
})
```

`site/tests/SiteHeader.spec.ts`:

```ts
import { afterEach, describe, expect, it } from "vitest"
import SiteHeader from "../src/components/layout/SiteHeader.vue"
import { i18n } from "../src/i18n"
import { montar, texto } from "./montar"

describe("SiteHeader", () => {
  afterEach(() => localStorage.clear())

  it("mostra a navegação em português", async () => {
    const w = await montar(SiteHeader)
    expect(texto(w)).toContain("Sobre")
    expect(texto(w)).toContain("Projetos")
    expect(w.find("nav a[href='/dados-combustiveis']").exists()).toBe(true)
  })

  it("troca para inglês, ajusta o lang e salva a escolha", async () => {
    const w = await montar(SiteHeader)
    await w.get("[data-testid='trocar-idioma']").trigger("click")
    expect(i18n.global.locale.value).toBe("en")
    expect(texto(w)).toContain("About")
    expect(document.documentElement.lang).toBe("en")
    expect(localStorage.getItem("idioma")).toBe("en")
  })

  it("menu móvel abre e fecha", async () => {
    const w = await montar(SiteHeader)
    const botao = w.get("[data-testid='menu']")
    expect(botao.attributes("aria-expanded")).toBe("false")
    await botao.trigger("click")
    expect(botao.attributes("aria-expanded")).toBe("true")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/router.spec.ts tests/SiteHeader.spec.ts`
Esperado: FALHA. O `router.spec` não encontra a rota `dados` e o `SiteHeader.spec` não resolve o componente.

- [ ] **Passo 3: Implementar rotas, SEO, app e esqueletos das views**

`site/src/router.ts` (substituir o provisório):

```ts
import { createRouter, createWebHistory, type RouterHistory } from "vue-router"
import HomeView from "./views/HomeView.vue"

export function criarRouter(history: RouterHistory = createWebHistory(import.meta.env.BASE_URL)) {
  return createRouter({
    history,
    routes: [
      { path: "/", name: "home", component: HomeView },
      { path: "/dados-combustiveis", name: "dados", component: () => import("./views/FuelDataView.vue") },
      { path: "/:caminho(.*)*", redirect: "/" },
    ],
    scrollBehavior(to, _from, salvo) {
      if (salvo) return salvo
      if (to.hash) return { el: to.hash }
      return { top: 0 }
    },
  })
}
```

`site/src/lib/seo.ts`:

```ts
import type { Idioma } from "../i18n"

function definirMeta(atributo: "name" | "property", chave: string, valor: string): void {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[${atributo}="${chave}"]`)
  if (!el) {
    el = document.createElement("meta")
    el.setAttribute(atributo, chave)
    document.head.appendChild(el)
  }
  el.setAttribute("content", valor)
}

export function aplicarMeta({ titulo, descricao, idioma }: { titulo: string; descricao: string; idioma: Idioma }): void {
  document.title = titulo
  definirMeta("name", "description", descricao)
  definirMeta("property", "og:title", titulo)
  definirMeta("property", "og:description", descricao)
  definirMeta("property", "og:locale", idioma === "pt" ? "pt_BR" : "en_US")
}
```

`site/src/main.ts`:

```ts
import "@fontsource-variable/inter"
import "./styles/tokens.css"
import "./styles/base.css"
import { createApp } from "vue"
import App from "./App.vue"
import { aplicarLang, i18n, type Idioma } from "./i18n"
import { criarRouter } from "./router"

aplicarLang(i18n.global.locale.value as Idioma)
createApp(App).use(i18n).use(criarRouter()).mount("#app")
```

`site/src/App.vue`:

```vue
<script setup lang="ts">
import SiteFooter from "./components/layout/SiteFooter.vue"
import SiteHeader from "./components/layout/SiteHeader.vue"
</script>

<template>
  <SiteHeader />
  <!-- altura mínima: enquanto a rota carregada sob demanda chega, o rodapé fica fora da tela e não "pula" (CLS) -->
  <div class="app__rota">
    <RouterView />
  </div>
  <SiteFooter />
</template>

<style scoped>
.app__rota { min-height: 100vh; }
</style>
```

`site/src/views/HomeView.vue` (esqueleto):

```vue
<script setup lang="ts">
import { watchEffect } from "vue"
import { useI18n } from "vue-i18n"
import type { Idioma } from "../i18n"
import { aplicarMeta } from "../lib/seo"

const { t, locale } = useI18n()
watchEffect(() =>
  aplicarMeta({ titulo: t("meta.tituloHome"), descricao: t("meta.descricaoHome"), idioma: locale.value as Idioma }),
)
</script>

<template>
  <main id="conteudo"></main>
</template>
```

`site/src/views/FuelDataView.vue` (esqueleto):

```vue
<script setup lang="ts">
import { watchEffect } from "vue"
import { useI18n } from "vue-i18n"
import type { Idioma } from "../i18n"
import { aplicarMeta } from "../lib/seo"

const { t, locale } = useI18n()
watchEffect(() =>
  aplicarMeta({ titulo: t("meta.tituloDados"), descricao: t("meta.descricaoDados"), idioma: locale.value as Idioma }),
)
</script>

<template>
  <main id="conteudo" class="container"></main>
</template>
```

- [ ] **Passo 4: Implementar cabeçalho e rodapé**

`site/src/components/layout/SiteHeader.vue`:

```vue
<script setup lang="ts">
import { ref } from "vue"
import { useI18n } from "vue-i18n"
import { definirIdioma } from "../../i18n"

const { t, locale } = useI18n()
const menuAberto = ref(false)
const ancoras = ["sobre", "experiencia", "projetos"] as const

function alternarIdioma(): void {
  definirIdioma(locale.value === "pt" ? "en" : "pt")
}
</script>

<template>
  <a class="pular" href="#conteudo">{{ t("nav.pularConteudo") }}</a>
  <header class="cabecalho">
    <div class="container cabecalho__barra">
      <RouterLink to="/" class="cabecalho__marca">Davi Levy</RouterLink>
      <button
        type="button"
        class="cabecalho__menu botao botao--secundario"
        data-testid="menu"
        :aria-expanded="menuAberto"
        aria-controls="nav-principal"
        @click="menuAberto = !menuAberto"
      >
        {{ t("nav.menu") }}
      </button>
      <nav id="nav-principal" class="cabecalho__nav" :class="{ 'cabecalho__nav--aberta': menuAberto }" :aria-label="t('nav.rotulo')">
        <RouterLink v-for="a in ancoras" :key="a" :to="{ path: '/', hash: `#${a}` }" @click="menuAberto = false">
          {{ t(`nav.${a}`) }}
        </RouterLink>
        <RouterLink to="/dados-combustiveis" @click="menuAberto = false">{{ t("nav.dados") }}</RouterLink>
        <RouterLink :to="{ path: '/', hash: '#contato' }" @click="menuAberto = false">{{ t("nav.contato") }}</RouterLink>
      </nav>
      <button
        type="button"
        class="cabecalho__idioma botao botao--secundario"
        data-testid="trocar-idioma"
        :aria-label="t('nav.idiomaRotulo')"
        @click="alternarIdioma"
      >
        {{ t("nav.idiomaCurto") }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.cabecalho {
  position: sticky; top: 0; z-index: 50;
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--cor-borda);
}
.cabecalho__barra { display: flex; align-items: center; gap: 0.75rem; min-height: 64px; flex-wrap: wrap; }
.cabecalho__marca { font-weight: 700; color: var(--cor-texto-forte); text-decoration: none; margin-right: auto; }
.cabecalho__nav { display: none; width: 100%; flex-direction: column; padding-bottom: 0.75rem; order: 3; }
.cabecalho__nav--aberta { display: flex; }
.cabecalho__nav a {
  color: var(--cor-texto); text-decoration: none; padding: 0.625rem 0.25rem;
  min-height: 44px; display: flex; align-items: center;
}
.cabecalho__nav a:hover { color: var(--cor-azul); }
@media (min-width: 900px) {
  .cabecalho__menu { display: none; }
  .cabecalho__nav { display: flex; flex-direction: row; width: auto; padding: 0; order: 0; gap: 1.25rem; }
}
</style>
```

`site/src/components/layout/SiteFooter.vue`:

```vue
<script setup lang="ts">
import { useI18n } from "vue-i18n"
import { perfil } from "../../content/perfil"

const { t } = useI18n()
const ano = new Date().getFullYear()
</script>

<template>
  <footer class="rodape">
    <div class="container rodape__conteudo">
      <p>© {{ ano }} Davi Levy · {{ t("rodape.texto") }}</p>
      <a :href="perfil.repoPortfolio" target="_blank" rel="noopener">{{ t("rodape.codigo") }}</a>
    </div>
  </footer>
</template>

<style scoped>
.rodape { border-top: 1px solid var(--cor-borda); padding-block: 2rem; color: var(--cor-texto-suave); font-size: 0.875rem; }
.rodape__conteudo { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 0.5rem 1.5rem; }
.rodape p { margin: 0; }
</style>
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam.

- [ ] **Passo 6: Conferir no navegador**

Rodar: `cd site && npm run dev` e abrir `http://localhost:5173/`.
Esperado: o cabeçalho aparece com o fundo azul-marinho. O botão EN/PT alterna os textos. Abaixo de 900 px aparece o botão "Menu". Encerre o servidor com Ctrl+C.

- [ ] **Passo 7: Commit**

```bash
cd site
git add src/router.ts src/main.ts src/App.vue src/lib/seo.ts src/components/layout src/views tests/router.spec.ts tests/SiteHeader.spec.ts
git commit -m "feat(site): rotas, cabeçalho bilíngue, rodapé e metadados" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 5: Hero, Sobre e Experiência

**Arquivos:**
- Criar: `site/src/components/home/HeroSection.vue`, `AboutSection.vue`, `ExperienceSection.vue`
- Modificar: `site/src/views/HomeView.vue`
- Criar: `site/tests/HeroSection.spec.ts`, `site/tests/AboutExperience.spec.ts`

**Interfaces:**
- Consome: `useConteudo`, `useFuelData<Meta>("meta.json")`, `perfil`, `cv`, `stack`, `projetos` e `formatarReais`.
- Produz: as seções com os ids `sobre` e `experiencia`. O item de gasolina do hero tem `data-testid="gasolina-df"`.

- [ ] **Passo 1: Escrever os testes que falham**

`site/tests/HeroSection.spec.ts`:

```ts
import { afterEach, describe, expect, it } from "vitest"
import meta from "../src/__fixtures__/meta.json"
import HeroSection from "../src/components/home/HeroSection.vue"
import { cv } from "../src/content/perfil"
import { montar, simularDados, texto } from "./montar"

describe("HeroSection", () => {
  afterEach(() => {
    cv.pt = null
    cv.en = null
  })

  it("mostra frase, números e o preço da gasolina no DF", async () => {
    simularDados({ "meta.json": meta })
    const w = await montar(HeroSection)
    expect(w.get("h1").text()).toBe("Código que resolve. Dados que explicam.")
    expect(w.findAll(".numero__valor").map((e) => texto(e))).toEqual(["2+", "6", "R$ 6,67"])
    expect(texto(w)).toContain("projetos em destaque")
    expect(texto(w.get("[data-testid='gasolina-df']"))).toContain("gasolina no DF hoje")
  })

  it("sem dados, esconde só o número da gasolina", async () => {
    simularDados({})
    const w = await montar(HeroSection)
    expect(w.find("[data-testid='gasolina-df']").exists()).toBe(false)
    expect(w.findAll(".numero__valor").map((e) => e.text())).toEqual(["2+", "6"])
  })

  it("botão de CV só aparece quando o arquivo existe", async () => {
    simularDados({})
    expect((await montar(HeroSection)).text()).not.toContain("Baixar CV")
    cv.pt = "/cv/cv-pt.pdf"
    const w = await montar(HeroSection)
    expect(w.get("a[download]").attributes("href")).toBe("/cv/cv-pt.pdf")
  })

  it("em inglês", async () => {
    simularDados({ "meta.json": meta })
    const w = await montar(HeroSection, { idioma: "en" })
    expect(w.get("h1").text()).toBe("Code that solves. Data that explains.")
    expect(w.get("[data-testid='gasolina-df']").text()).toContain("R$6.67")
  })
})
```

`site/tests/AboutExperience.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import AboutSection from "../src/components/home/AboutSection.vue"
import ExperienceSection from "../src/components/home/ExperienceSection.vue"
import { montar, texto } from "./montar"

describe("Sobre", () => {
  it("mostra stack agrupada, formação e certificações", async () => {
    const w = await montar(AboutSection)
    expect(w.attributes("id")).toBe("sobre")
    for (const t of ["Front-end", "Back-end", "Dados/IA", "DevOps", "PL/SQL (Oracle)", "Ciência da Computação", "Google AI Essentials"]) {
      expect(texto(w)).toContain(t)
    }
  })
})

describe("Experiência", () => {
  it("destaca a Rede SARAH com os cinco itens e lista as outras", async () => {
    const w = await montar(ExperienceSection)
    expect(w.attributes("id")).toBe("experiencia")
    expect(w.findAll("[data-testid='sarah'] li")).toHaveLength(5)
    expect(texto(w)).toContain("Zenit Aerospace")
    expect(texto(w)).toContain("Sabin Medicina Diagnóstica")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/HeroSection.spec.ts tests/AboutExperience.spec.ts`
Esperado: FALHA com `Failed to resolve import "../src/components/home/HeroSection.vue"`.

- [ ] **Passo 3: Implementar as três seções**

`site/src/components/home/HeroSection.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { useFuelData } from "../../composables/useFuelData"
import { cv, perfil, projetos } from "../../content/perfil"
import type { Idioma } from "../../i18n"
import { formatarReais } from "../../lib/format"
import type { Meta } from "../../types/dados"

const { t, locale } = useI18n()
const c = useConteudo()
const { dados: meta } = useFuelData<Meta>("meta.json")
const idioma = computed(() => locale.value as Idioma)
const arquivoCv = computed(() => cv[idioma.value])
const gasolinaDf = computed(() => (meta.value ? formatarReais(meta.value.destaques.gasolina_df, idioma.value) : null))
</script>

<template>
  <section class="hero" aria-labelledby="hero-titulo">
    <div class="container">
      <p class="hero__cargo">{{ perfil.nome }} · {{ c.hero.titulo }}</p>
      <h1 id="hero-titulo">{{ c.hero.frase1 }} <span class="hero__destaque">{{ c.hero.frase2 }}</span></h1>
      <p class="hero__resumo">{{ c.hero.resumo }}</p>
      <ul class="hero__numeros">
        <li class="numero">
          <span class="numero__valor">2+</span>
          <span class="numero__rotulo">{{ t("hero.statAnos") }}</span>
        </li>
        <li class="numero">
          <span class="numero__valor numero__valor--violeta">{{ projetos.length }}</span>
          <span class="numero__rotulo">{{ t("hero.statProjetos") }}</span>
        </li>
        <li v-if="gasolinaDf" class="numero" data-testid="gasolina-df">
          <span class="numero__valor numero__valor--verde">{{ gasolinaDf }}</span>
          <span class="numero__rotulo">{{ t("hero.statGasolina") }}</span>
        </li>
      </ul>
      <div class="hero__acoes">
        <a class="botao" href="#projetos">{{ t("hero.verProjetos") }}</a>
        <a v-if="arquivoCv" class="botao botao--secundario" :href="arquivoCv" download>{{ t("hero.baixarCv") }}</a>
        <a class="botao botao--secundario" :href="perfil.github" target="_blank" rel="noopener">GitHub</a>
        <a class="botao botao--secundario" :href="perfil.linkedin" target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero { padding-block: clamp(3rem, 10vw, 6rem) clamp(2.5rem, 8vw, 4rem); }
.hero__cargo { color: var(--cor-texto-suave); font-weight: 500; }
.hero__destaque { color: var(--cor-azul); display: block; }
.hero__resumo { font-size: 1.125rem; max-width: 60ch; color: var(--cor-texto); }
.hero__numeros {
  list-style: none; padding: 0; margin: 2rem 0;
  display: grid; gap: 0.75rem; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); max-width: 720px;
}
.numero { background: var(--cor-superficie); border: 1px solid var(--cor-borda); border-radius: var(--raio); padding: 1rem; }
.numero__valor { display: block; font-size: 1.75rem; font-weight: 700; color: var(--cor-azul); font-variant-numeric: tabular-nums; }
.numero__valor--violeta { color: var(--cor-violeta); }
.numero__valor--verde { color: var(--cor-verde); }
.numero__rotulo { font-size: 0.875rem; color: var(--cor-texto-suave); }
.hero__acoes { display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>
```

`site/src/components/home/AboutSection.vue`:

```vue
<script setup lang="ts">
import { useConteudo } from "../../composables/useConteudo"
import { type GrupoStack, stack } from "../../content/perfil"

const c = useConteudo()
const grupos = Object.keys(stack) as GrupoStack[]
</script>

<template>
  <section id="sobre" class="secao" aria-labelledby="sobre-titulo">
    <div class="container sobre">
      <div>
        <h2 id="sobre-titulo">{{ c.sobre.titulo }}</h2>
        <p v-for="(paragrafo, i) in c.sobre.paragrafos" :key="i">{{ paragrafo }}</p>
        <h3>{{ c.sobre.formacaoTitulo }}</h3>
        <ul class="lista">
          <li v-for="f in c.sobre.formacao" :key="f.instituicao">
            <strong>{{ f.curso }}</strong> — {{ f.instituicao }}<span v-if="f.periodo" class="suave"> · {{ f.periodo }}</span>
          </li>
        </ul>
        <h3>{{ c.sobre.certificacoesTitulo }}</h3>
        <ul class="lista">
          <li v-for="item in c.sobre.certificacoes" :key="item">{{ item }}</li>
        </ul>
        <h3>{{ c.sobre.idiomasTitulo }}</h3>
        <ul class="lista">
          <li v-for="item in c.sobre.idiomas" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="cartao">
        <h3>{{ c.sobre.stackTitulo }}</h3>
        <div v-for="g in grupos" :key="g" class="stack__grupo">
          <p class="stack__rotulo">{{ c.sobre.grupos[g] }}</p>
          <ul class="etiquetas">
            <li v-for="tec in stack[g]" :key="tec">{{ tec }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sobre { display: grid; gap: 2rem; }
@media (min-width: 900px) { .sobre { grid-template-columns: 3fr 2fr; align-items: start; } }
.lista { padding-left: 1.1rem; margin: 0 0 1.25rem; }
.stack__grupo + .stack__grupo { margin-top: 1rem; }
.stack__rotulo { font-size: 0.8125rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--cor-texto-suave); margin-bottom: 0.5rem; }
</style>
```

`site/src/components/home/ExperienceSection.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue"
import { useConteudo } from "../../composables/useConteudo"

const c = useConteudo()
const destaque = computed(() => c.value.experiencia.destaque)
</script>

<template>
  <section id="experiencia" class="secao" aria-labelledby="experiencia-titulo">
    <div class="container">
      <h2 id="experiencia-titulo">{{ c.experiencia.titulo }}</h2>
      <article class="cartao experiencia" data-testid="sarah">
        <p class="experiencia__periodo">{{ destaque.periodo }} · {{ destaque.local }}</p>
        <h3>{{ destaque.cargo }}</h3>
        <p class="experiencia__empresa">{{ destaque.empresa }}</p>
        <ul>
          <li v-for="(item, i) in destaque.itens" :key="i">{{ item }}</li>
        </ul>
      </article>
      <h3 class="outras__titulo">{{ c.experiencia.outrasTitulo }}</h3>
      <ul class="outras">
        <li v-for="o in c.experiencia.outras" :key="o.empresa">
          <strong>{{ o.cargo }}</strong> — {{ o.empresa }} <span class="suave">· {{ o.periodo }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.experiencia { border-left: 4px solid var(--cor-azul); }
.experiencia__periodo { font-size: 0.875rem; color: var(--cor-texto-suave); margin-bottom: 0.25rem; }
.experiencia__empresa { color: var(--cor-azul); font-weight: 500; }
.experiencia ul { padding-left: 1.1rem; margin: 0; display: grid; gap: 0.5rem; }
.outras__titulo { margin-top: 2rem; }
.outras { padding-left: 1.1rem; }
</style>
```

- [ ] **Passo 4: Colocar as seções na home**

`site/src/views/HomeView.vue`:

```vue
<script setup lang="ts">
import { watchEffect } from "vue"
import { useI18n } from "vue-i18n"
import AboutSection from "../components/home/AboutSection.vue"
import ExperienceSection from "../components/home/ExperienceSection.vue"
import HeroSection from "../components/home/HeroSection.vue"
import type { Idioma } from "../i18n"
import { aplicarMeta } from "../lib/seo"

const { t, locale } = useI18n()
watchEffect(() =>
  aplicarMeta({ titulo: t("meta.tituloHome"), descricao: t("meta.descricaoHome"), idioma: locale.value as Idioma }),
)
</script>

<template>
  <main id="conteudo">
    <HeroSection />
    <AboutSection />
    <ExperienceSection />
  </main>
</template>
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam.

- [ ] **Passo 6: Commit**

```bash
cd site
git add src/components/home src/views/HomeView.vue tests/HeroSection.spec.ts tests/AboutExperience.spec.ts
git commit -m "feat(site): hero, sobre e experiência" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 6: Projetos

**Arquivos:**
- Criar: `site/src/components/home/ProjectCard.vue`, `site/src/components/home/ProjectsSection.vue`
- Modificar: `site/src/views/HomeView.vue` (acrescentar `<ProjectsSection />` depois de `<ExperienceSection />`)
- Criar: `site/tests/ProjectsSection.spec.ts`

**Interfaces:**
- Consome: `projetos` e `perfil` (Tarefa 2) e `useConteudo`.
- Produz: a seção com id `projetos` e um `article[data-testid="projeto-<id>"]` por projeto.

- [ ] **Passo 1: Escrever o teste que falha**

`site/tests/ProjectsSection.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import ProjectsSection from "../src/components/home/ProjectsSection.vue"
import { montar, texto } from "./montar"

describe("ProjectsSection", () => {
  it("mostra os seis projetos na ordem, cada um com o papel", async () => {
    const w = await montar(ProjectsSection)
    const cards = w.findAll("article")
    expect(cards.map((c) => c.attributes("data-testid"))).toEqual([
      "projeto-nodus", "projeto-forunb", "projeto-soma", "projeto-anp", "projeto-flowpad", "projeto-compiladores",
    ])
    for (const card of cards) expect(card.text()).toContain("Meu papel")
  })

  it("NODUS descreve o app desktop offline e o papel de gerente/Scrum Master", async () => {
    const w = await montar(ProjectsSection)
    const nodus = texto(w.get("[data-testid='projeto-nodus']"))
    expect(nodus).toContain("Electron")
    expect(nodus).toContain("Scrum Master")
    expect(w.get("[data-testid='projeto-nodus'] a[href*='cathsatile/NODUS']").attributes("target")).toBe("_blank")
  })

  it("o card da ANP tem link interno para a análise", async () => {
    const w = await montar(ProjectsSection)
    expect(w.find("[data-testid='projeto-anp'] a[href='/dados-combustiveis']").exists()).toBe(true)
  })

  it("tem link para todos os repositórios", async () => {
    const w = await montar(ProjectsSection)
    expect(w.find("a[href='https://github.com/Davi-KL?tab=repositories']").exists()).toBe(true)
  })

  it("em inglês", async () => {
    const w = await montar(ProjectsSection, { idioma: "en" })
    expect(texto(w)).toContain("My role")
    expect(texto(w)).toContain("Portugol Lexical Analyzer")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/ProjectsSection.spec.ts`
Esperado: FALHA com `Failed to resolve import "../src/components/home/ProjectsSection.vue"`.

- [ ] **Passo 3: Implementar**

`site/src/components/home/ProjectCard.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import type { Projeto } from "../../content/perfil"

const props = defineProps<{ projeto: Projeto }>()
const { t } = useI18n()
const c = useConteudo()
const item = computed(() => c.value.projetos.itens[props.projeto.id])
</script>

<template>
  <article class="cartao projeto" :data-testid="`projeto-${projeto.id}`">
    <h3>{{ item.titulo }}</h3>
    <p class="projeto__descricao">{{ item.descricao }}</p>
    <p class="projeto__papel"><strong>{{ t("projetos.papel") }}:</strong> {{ item.papel }}</p>
    <ul class="etiquetas">
      <li v-for="tag in projeto.tags" :key="tag">{{ tag }}</li>
    </ul>
    <div class="projeto__links">
      <template v-for="link in projeto.links" :key="link.url">
        <RouterLink v-if="link.interno" class="botao" :to="link.url">{{ t(`projetos.links.${link.tipo}`) }}</RouterLink>
        <a v-else class="botao botao--secundario" :href="link.url" target="_blank" rel="noopener">
          {{ t(`projetos.links.${link.tipo}`) }}
        </a>
      </template>
    </div>
  </article>
</template>

<style scoped>
.projeto { display: flex; flex-direction: column; gap: 0.75rem; }
.projeto h3 { margin: 0; }
.projeto__descricao { margin: 0; color: var(--cor-texto); }
.projeto__papel { margin: 0; font-size: 0.9375rem; color: var(--cor-texto-suave); }
.projeto__papel strong { color: var(--cor-verde); }
.projeto__links { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: auto; padding-top: 0.5rem; }
</style>
```

`site/src/components/home/ProjectsSection.vue`:

```vue
<script setup lang="ts">
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { perfil, projetos } from "../../content/perfil"
import ProjectCard from "./ProjectCard.vue"

const { t } = useI18n()
const c = useConteudo()
</script>

<template>
  <section id="projetos" class="secao" aria-labelledby="projetos-titulo">
    <div class="container">
      <h2 id="projetos-titulo">{{ c.projetos.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.projetos.subtitulo }}</p>
      <div class="projetos__grade">
        <ProjectCard v-for="p in projetos" :key="p.id" :projeto="p" />
      </div>
      <p class="projetos__todos">
        <a :href="perfil.repositorios" target="_blank" rel="noopener">{{ t("projetos.verTodos") }} →</a>
      </p>
    </div>
  </section>
</template>

<style scoped>
.projetos__grade { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); }
.projetos__todos { margin-top: 1.5rem; }
</style>
```

Em `site/src/views/HomeView.vue`, acrescentar o import `import ProjectsSection from "../components/home/ProjectsSection.vue"` e a tag `<ProjectsSection />` logo depois de `<ExperienceSection />`.

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam.

- [ ] **Passo 5: Commit**

```bash
cd site
git add src/components/home/ProjectCard.vue src/components/home/ProjectsSection.vue src/views/HomeView.vue tests/ProjectsSection.spec.ts
git commit -m "feat(site): seção de projetos com papel em cada card" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 7: Prévia da análise (minigráfico) e Contato

**Arquivos:**
- Criar: `site/src/lib/sparkline.ts`
- Criar: `site/src/components/home/FuelPreviewSection.vue`, `site/src/components/home/ContactSection.vue`
- Modificar: `site/src/views/HomeView.vue` (acrescentar `<FuelPreviewSection />` e `<ContactSection />` depois de `<ProjectsSection />`)
- Criar: `site/tests/sparkline.spec.ts`, `site/tests/FuelPreviewContact.spec.ts`

**Interfaces:**
- Produz:
  - `dominio(series: readonly Serie[]): [number, number] | null`.
  - `caminhoSparkline(valores: Serie, largura: number, altura: number, dom: [number, number], margem = 4): string`, que gera o atributo `d` de um `<path>` SVG; `null` interrompe a linha.
  - A seção `#dados` (`data-testid="previa-anp"`), que só aparece com dados.
  - A seção `#contato`.

- [ ] **Passo 1: Escrever os testes que falham**

`site/tests/sparkline.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import { caminhoSparkline, dominio } from "../src/lib/sparkline"

describe("sparkline", () => {
  it("domínio conjunto ignora nulos", () => {
    expect(dominio([[1, null, 3], [2, 5]])).toEqual([1, 5])
    expect(dominio([[null]])).toBeNull()
  })

  it("desenha pontos na escala", () => {
    expect(caminhoSparkline([1, 2, 3], 104, 24, [1, 3])).toBe("M4.0,20.0 L52.0,12.0 L100.0,4.0")
  })

  it("interrompe a linha em buracos", () => {
    expect(caminhoSparkline([1, null, 3], 104, 24, [1, 3])).toBe("M4.0,20.0 M100.0,4.0")
  })

  it("série constante fica na base", () => {
    expect(caminhoSparkline([2, 2], 104, 24, [2, 2])).toBe("M4.0,20.0 L100.0,20.0")
  })

  it("menos de dois pontos não desenha", () => {
    expect(caminhoSparkline([2], 104, 24, [2, 2])).toBe("")
  })
})
```

`site/tests/FuelPreviewContact.spec.ts`:

```ts
import { afterEach, describe, expect, it } from "vitest"
import meta from "../src/__fixtures__/meta.json"
import ContactSection from "../src/components/home/ContactSection.vue"
import FuelPreviewSection from "../src/components/home/FuelPreviewSection.vue"
import { cv } from "../src/content/perfil"
import { montar, simularDados, texto } from "./montar"

describe("Prévia da análise", () => {
  it("mostra três insights, minigráfico e link para a análise", async () => {
    simularDados({ "meta.json": meta })
    const w = await montar(FuelPreviewSection)
    expect(w.findAll("li")).toHaveLength(3)
    expect(texto(w)).toContain("+1,7% em relação à média nacional")
    expect(texto(w)).toContain("O etanol compensa em 11 dos 27 estados")
    expect(texto(w)).toContain("diesel S10 em AC (+8,1%)")
    expect(w.findAll("svg path")).toHaveLength(2)
    expect(w.find("a[href='/dados-combustiveis']").exists()).toBe(true)
  })

  it("some por completo se os dados falharem", async () => {
    simularDados({ "meta.json": 500 })
    const w = await montar(FuelPreviewSection)
    expect(w.find("[data-testid='previa-anp']").exists()).toBe(false)
  })

  it("sem maior alta, mostra só dois insights", async () => {
    simularDados({ "meta.json": { ...meta, destaques: { ...meta.destaques, maior_alta_12m: null } } })
    const w = await montar(FuelPreviewSection)
    expect(w.findAll("li")).toHaveLength(2)
  })
})

describe("Contato", () => {
  afterEach(() => {
    cv.pt = null
  })

  it("tem e-mail, LinkedIn e GitHub; CV só com arquivo", async () => {
    const w = await montar(ContactSection)
    expect(w.attributes("id")).toBe("contato")
    expect(w.get("[data-testid='contato-email']").attributes("href")).toBe("mailto:daviklevy@gmail.com")
    expect(w.find("a[href='https://www.linkedin.com/in/davi-levy-dev']").exists()).toBe(true)
    expect(w.find("a[href='https://github.com/Davi-KL']").exists()).toBe(true)
    expect(w.find("[data-testid='contato-cv']").exists()).toBe(false)
    cv.pt = "/cv/cv-pt.pdf"
    const comCv = await montar(ContactSection)
    expect(comCv.get("[data-testid='contato-cv']").attributes("href")).toBe("/cv/cv-pt.pdf")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/sparkline.spec.ts tests/FuelPreviewContact.spec.ts`
Esperado: FALHA com `Failed to resolve import`.

- [ ] **Passo 3: Implementar `sparkline.ts`**

`site/src/lib/sparkline.ts`:

```ts
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
```

- [ ] **Passo 4: Implementar as seções**

`site/src/components/home/FuelPreviewSection.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { useFuelData } from "../../composables/useFuelData"
import type { Idioma } from "../../i18n"
import { formatarPct, formatarReais } from "../../lib/format"
import { caminhoSparkline, dominio } from "../../lib/sparkline"
import type { Meta } from "../../types/dados"

const LARGURA = 320
const ALTURA = 96

const { t, locale } = useI18n()
const c = useConteudo()
const { dados: meta } = useFuelData<Meta>("meta.json")
const idioma = computed(() => locale.value as Idioma)

const caminhos = computed(() => {
  if (!meta.value) return null
  const { gasolina_br, gasolina_df } = meta.value.serie_home
  const dom = dominio([gasolina_br, gasolina_df])
  if (!dom) return null
  return {
    br: caminhoSparkline(gasolina_br, LARGURA, ALTURA, dom),
    df: caminhoSparkline(gasolina_df, LARGURA, ALTURA, dom),
  }
})

const insights = computed(() => {
  if (!meta.value) return []
  const d = meta.value.destaques
  const i = idioma.value
  const lista: string[] = []
  if (d.diff_df_br_pct !== null) {
    lista.push(t("previa.insightDf", { preco: formatarReais(d.gasolina_df, i), pct: formatarPct(d.diff_df_br_pct, i) }))
  }
  lista.push(t("previa.insightEtanol", { n: d.ufs_etanol_compensa }))
  if (d.maior_alta_12m) {
    lista.push(
      t("previa.insightAlta", {
        produto: t(`produtos.${d.maior_alta_12m.produto}`),
        uf: d.maior_alta_12m.uf,
        pct: formatarPct(d.maior_alta_12m.pct, i),
      }),
    )
  }
  return lista
})
</script>

<template>
  <section v-if="meta" id="dados" class="secao" aria-labelledby="previa-titulo" data-testid="previa-anp">
    <div class="container previa">
      <div>
        <h2 id="previa-titulo">{{ c.previa.titulo }}</h2>
        <p class="secao__subtitulo">{{ c.previa.subtitulo }}</p>
        <ul class="previa__insights">
          <li v-for="(insight, k) in insights" :key="k">{{ insight }}</li>
        </ul>
        <RouterLink class="botao" to="/dados-combustiveis">{{ t("previa.verAnalise") }} →</RouterLink>
      </div>
      <figure v-if="caminhos" class="cartao previa__grafico">
        <svg :viewBox="`0 0 ${LARGURA} ${ALTURA}`" role="img" :aria-label="t('previa.graficoRotulo')" preserveAspectRatio="none">
          <path :d="caminhos.br" fill="none" stroke="var(--cor-azul)" stroke-width="2.5" vector-effect="non-scaling-stroke" />
          <path :d="caminhos.df" fill="none" stroke="var(--cor-ambar)" stroke-width="2" vector-effect="non-scaling-stroke" />
        </svg>
        <figcaption class="previa__legenda">
          <span class="chave chave--br" aria-hidden="true"></span>{{ t("previa.brasil") }}
          <span class="chave chave--df" aria-hidden="true"></span>{{ t("previa.df") }}
        </figcaption>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.previa { display: grid; gap: 2rem; align-items: center; }
@media (min-width: 900px) { .previa { grid-template-columns: 3fr 2fr; } }
.previa__insights { padding-left: 1.1rem; display: grid; gap: 0.5rem; margin: 0 0 1.5rem; }
.previa__grafico { margin: 0; }
.previa__grafico svg { width: 100%; height: 140px; }
.previa__legenda { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--cor-texto-suave); margin-top: 0.75rem; }
.chave { display: inline-block; width: 16px; height: 3px; border-radius: 2px; }
.chave--br { background: var(--cor-azul); }
.chave--df { background: var(--cor-ambar); margin-left: 0.75rem; }
</style>
```

`site/src/components/home/ContactSection.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { cv, perfil } from "../../content/perfil"
import type { Idioma } from "../../i18n"

const { t, locale } = useI18n()
const c = useConteudo()
const arquivoCv = computed(() => cv[locale.value as Idioma])
</script>

<template>
  <section id="contato" class="secao" aria-labelledby="contato-titulo">
    <div class="container">
      <h2 id="contato-titulo">{{ c.contato.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.contato.texto }}</p>
      <ul class="contato__links">
        <li>
          <a class="botao" :href="`mailto:${perfil.email}`" data-testid="contato-email">{{ t("contato.email") }}: {{ perfil.email }}</a>
        </li>
        <li><a class="botao botao--secundario" :href="perfil.linkedin" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a class="botao botao--secundario" :href="perfil.github" target="_blank" rel="noopener">GitHub</a></li>
        <li v-if="arquivoCv">
          <a class="botao botao--secundario" :href="arquivoCv" download data-testid="contato-cv">{{ t("contato.cv") }}</a>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.contato__links { list-style: none; padding: 0; margin: 1.5rem 0 0; display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>
```

Em `site/src/views/HomeView.vue`, acrescentar os imports de `FuelPreviewSection` e `ContactSection` e as tags `<FuelPreviewSection />` e `<ContactSection />`, nessa ordem, depois de `<ProjectsSection />`.

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam.

- [ ] **Passo 6: Conferir no navegador com os dados reais**

Rodar: `cd site && npm run dev` e abrir `http://localhost:5173/`. Os dados reais da Parte 1 já estão em `public/data/`.
Esperado: a home completa, com o hero mostrando a gasolina no DF, os 6 projetos, a prévia com o minigráfico e o contato. Encerre com Ctrl+C.

- [ ] **Passo 7: Commit**

```bash
cd site
git add src/lib/sparkline.ts src/components/home/FuelPreviewSection.vue src/components/home/ContactSection.vue src/views/HomeView.vue tests/sparkline.spec.ts tests/FuelPreviewContact.spec.ts
git commit -m "feat(site): prévia da análise com minigráfico e seção de contato" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 8: Lógica dos gráficos e insights (funções puras)

**Arquivos:**
- Criar: `site/src/lib/chartTheme.ts`, `site/src/lib/graficos.ts`, `site/src/lib/insights.ts`
- Criar: `site/tests/graficos.spec.ts`

**Interfaces:**
- Consome: os tipos de `src/types/dados.ts` e os fixtures.
- Produz:
  - `chartTheme.ts`: `CORES_PRODUTO`, `COR_DESTAQUE`, `COR_REFERENCIA`, `LAYOUT_BASE`, `CONFIG_BASE` e `mesclarLayout(extra, altura): Record<string, unknown>`.
  - `graficos.ts`:
    - os tipos `Traco`, `Modo` e `Tabela`;
    - `serieEvolucao(evo, regiao, produto, modo)`;
    - `tracosEvolucao(evo, produto, uf, modo, nomes: { brasil; uf })`;
    - `tabelaEvolucao(evo, produto, uf, modo, cab: { mes; brasil; uf }, fmtMes, fmtValor)`;
    - `itensRanking(r, produto)`, em ordem decrescente e sem BR;
    - `tracosRanking(r, produto, fmtVar, destaque = "DF") -> { tracos; altura; referencia }`;
    - `tabelaRanking(r, produto, cab: { estado; preco; variacao; coletas }, fmtPreco, fmtVar)`;
    - `itensRazao(eg)`, em ordem crescente e sem BR;
    - `tracosRazaoAtual(eg, nomes: { etanol; gasolina }) -> { tracos; altura; ordem }`;
    - `tracosRazaoHistorico(eg, uf, nomes: { brasil; uf })`;
    - `tabelaRazao(eg, cab: { estado; razao; compensa }, fmtRazao, rotulos: { etanol; gasolina })`;
    - `linhaVertical(x)` e `linhaHorizontal(y)`.
  - `insights.ts`:
    - `insightEvolucao(evo, produto = "gasolina") -> { mesInicial; inicial; atual; variacaoPct } | null`, usando a série real do BR;
    - `insightRanking(r, produto, uf = "DF") -> { maisCara; maisBarata; posicao; total } | null`;
    - `ufsEtanol(eg): string[]`.

- [ ] **Passo 1: Escrever o teste que falha**

`site/tests/graficos.spec.ts`:

```ts
import { describe, expect, it } from "vitest"
import etanol from "../src/__fixtures__/etanol_gasolina.json"
import evolucao from "../src/__fixtures__/evolucao.json"
import ranking from "../src/__fixtures__/ranking_uf.json"
import { COR_DESTAQUE, CORES_PRODUTO, mesclarLayout } from "../src/lib/chartTheme"
import {
  tabelaEvolucao,
  tabelaRanking,
  tabelaRazao,
  tracosEvolucao,
  tracosRanking,
  tracosRazaoAtual,
  tracosRazaoHistorico,
} from "../src/lib/graficos"
import { insightEvolucao, insightRanking, ufsEtanol } from "../src/lib/insights"
import type { EtanolGasolina, Evolucao, Ranking } from "../src/types/dados"

const evo = evolucao as Evolucao
const rk = ranking as Ranking
const eg = etanol as EtanolGasolina

describe("evolução", () => {
  it("linha do Brasil na cor do produto e da UF em destaque", () => {
    const [br, df] = tracosEvolucao(evo, "gasolina", "DF", "real", { brasil: "Brasil", uf: "DF" })
    expect(br.y).toEqual([6.43, 6.48, 6.52, 6.558])
    expect((br.line as { color: string }).color).toBe(CORES_PRODUTO.gasolina)
    expect(df.name).toBe("DF")
    expect((df.line as { color: string }).color).toBe(COR_DESTAQUE)
  })

  it("com a UF igual a BR, uma linha só", () => {
    expect(tracosEvolucao(evo, "etanol", "BR", "nominal", { brasil: "Brasil", uf: "BR" })).toHaveLength(1)
  })

  it("UF sem série vira nulos em vez de quebrar", () => {
    const [, xx] = tracosEvolucao(evo, "gasolina", "XX", "real", { brasil: "Brasil", uf: "XX" })
    expect(xx.y).toEqual([null, null, null, null])
  })

  it("tabela do mês mais recente para o mais antigo, com traço nos buracos", () => {
    const tab = tabelaEvolucao(evo, "diesel_s10", "DF", "nominal", { mes: "Mês", brasil: "Brasil", uf: "DF" }, (m) => m, (v) => (v === null ? "—" : v.toFixed(2)))
    expect(tab.colunas).toEqual(["Mês", "Brasil", "DF"])
    expect(tab.linhas[0]).toEqual(["2026-09", "6.90", "6.95"])
    expect(tab.linhas[3]).toEqual(["2026-06", "6.80", "—"])
  })
})

describe("ranking", () => {
  const fmtVar = (v: number | null) => (v === null ? "—" : `${v}%`)

  it("barras do menor para o maior (maior no topo), DF em destaque, média BR como referência", () => {
    const { tracos, referencia } = tracosRanking(rk, "gasolina", fmtVar)
    expect(tracos[0].y).toEqual(["SP", "DF", "AC"])
    expect((tracos[0].marker as { color: string[] }).color).toEqual([CORES_PRODUTO.gasolina, COR_DESTAQUE, CORES_PRODUTO.gasolina])
    expect(tracos[0].customdata).toEqual(["2%", "2.9%", "5%"])
    expect(referencia).toBe(6.558)
  })

  it("tabela do mais caro para o mais barato", () => {
    const tab = tabelaRanking(rk, "etanol", { estado: "UF", preco: "Preço", variacao: "12m", coletas: "n" }, (v) => v.toFixed(2), fmtVar)
    expect(tab.linhas.map((l) => l[0])).toEqual(["AC", "DF", "SP"])
    expect(tab.linhas[1]).toEqual(["DF", "4.38", "—", "1100"])
  })
})

describe("etanol × gasolina", () => {
  it("separa quem compensa etanol e ordena com a menor razão no topo", () => {
    const { tracos, ordem } = tracosRazaoAtual(eg, { etanol: "Etanol", gasolina: "Gasolina" })
    expect(tracos[0].y).toEqual(["SP", "DF"])
    expect(tracos[1].y).toEqual(["AC"])
    // categoryarray do Plotly: o primeiro item fica embaixo, então a menor razão (SP) vai para o topo
    expect(ordem).toEqual(["AC", "DF", "SP"])
  })

  it("histórico com Brasil e a UF", () => {
    const [br, df] = tracosRazaoHistorico(eg, "DF", { brasil: "Brasil", uf: "DF" })
    expect(br.y).toEqual([0.655, 0.657, 0.656, 0.656])
    expect(df.y).toEqual([0.662, 0.661, null, 0.657])
  })

  it("tabela da menor para a maior razão", () => {
    const tab = tabelaRazao(eg, { estado: "UF", razao: "Razão", compensa: "Compensa" }, (v) => v.toFixed(3), { etanol: "Etanol", gasolina: "Gasolina" })
    expect(tab.linhas).toEqual([["SP", "0.594", "Etanol"], ["DF", "0.657", "Etanol"], ["AC", "0.725", "Gasolina"]])
  })
})

describe("insights", () => {
  it("evolução real da gasolina no Brasil", () => {
    const i = insightEvolucao(evo)
    expect(i?.mesInicial).toBe("2026-06")
    expect(i?.inicial).toBe(6.43)
    expect(i?.atual).toBe(6.558)
    expect(i?.variacaoPct).toBeCloseTo(1.99, 1)
  })

  it("ranking: mais cara, mais barata e posição do DF", () => {
    const i = insightRanking(rk, "gasolina")
    expect(i?.maisCara.uf).toBe("AC")
    expect(i?.maisBarata.uf).toBe("SP")
    expect(i?.posicao).toBe(2)
    expect(i?.total).toBe(3)
  })

  it("estados onde o etanol compensa, da menor razão para a maior", () => {
    expect(ufsEtanol(eg)).toEqual(["SP", "DF"])
  })
})

describe("layout", () => {
  it("mescla eixos sem perder o tema", () => {
    const l = mesclarLayout({ yaxis: { tickprefix: "R$ " } }, 400)
    expect(l.height).toBe(400)
    expect((l.yaxis as Record<string, unknown>).tickprefix).toBe("R$ ")
    expect((l.yaxis as Record<string, unknown>).gridcolor).toBe("#1e293b")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/graficos.spec.ts`
Esperado: FALHA com `Failed to resolve import "../src/lib/chartTheme"`.

- [ ] **Passo 3: Implementar `chartTheme.ts`**

`site/src/lib/chartTheme.ts`:

```ts
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
```

- [ ] **Passo 4: Implementar `graficos.ts`**

`site/src/lib/graficos.ts`:

```ts
import type { EtanolGasolina, Evolucao, ItemRanking, ItemRazao, Produto, Ranking, Serie } from "../types/dados"
import { COR_DESTAQUE, COR_REFERENCIA, CORES_PRODUTO } from "./chartTheme"

export type Traco = Record<string, unknown>
export type Modo = "nominal" | "real"
export interface Tabela {
  colunas: string[]
  linhas: string[][]
}
type FmtNulo = (valor: number | null) => string

export function serieEvolucao(evo: Evolucao, regiao: string, produto: Produto, modo: Modo): Serie {
  return evo.series[regiao]?.[produto]?.[modo] ?? evo.meses.map(() => null)
}

function linha(x: string[], y: Serie, nome: string, cor: string, largura: number, hover: string): Traco {
  return { type: "scatter", mode: "lines", name: nome, x, y, line: { color: cor, width: largura }, connectgaps: false, hovertemplate: hover }
}

export function tracosEvolucao(evo: Evolucao, produto: Produto, uf: string, modo: Modo, nomes: { brasil: string; uf: string }): Traco[] {
  const hover = "%{x|%m/%Y}: R$ %{y:.2f}<extra>%{fullData.name}</extra>"
  const tracos = [linha(evo.meses, serieEvolucao(evo, "BR", produto, modo), nomes.brasil, CORES_PRODUTO[produto], 2.5, hover)]
  if (uf !== "BR") tracos.push(linha(evo.meses, serieEvolucao(evo, uf, produto, modo), nomes.uf, COR_DESTAQUE, 2, hover))
  return tracos
}

export function tabelaEvolucao(
  evo: Evolucao, produto: Produto, uf: string, modo: Modo,
  cab: { mes: string; brasil: string; uf: string }, fmtMes: (mes: string) => string, fmtValor: FmtNulo,
): Tabela {
  const br = serieEvolucao(evo, "BR", produto, modo)
  const local = serieEvolucao(evo, uf, produto, modo)
  const linhas = evo.meses.map((m, i) => [fmtMes(m), fmtValor(br[i]), fmtValor(local[i])]).reverse()
  return { colunas: [cab.mes, cab.brasil, cab.uf], linhas }
}

export function itensRanking(r: Ranking, produto: Produto): ItemRanking[] {
  return r.itens.filter((i) => i.produto === produto && i.uf !== "BR").sort((a, b) => b.preco_medio - a.preco_medio)
}

export function tracosRanking(r: Ranking, produto: Produto, fmtVar: FmtNulo, destaque = "DF"): { tracos: Traco[]; altura: number; referencia: number | null } {
  const itens = [...itensRanking(r, produto)].reverse()
  return {
    tracos: [{
      type: "bar",
      orientation: "h",
      x: itens.map((i) => i.preco_medio),
      y: itens.map((i) => i.uf),
      marker: { color: itens.map((i) => (i.uf === destaque ? COR_DESTAQUE : CORES_PRODUTO[produto])) },
      customdata: itens.map((i) => fmtVar(i.variacao_12m_pct)),
      hovertemplate: "%{y}: R$ %{x:.2f} · 12m: %{customdata}<extra></extra>",
    }],
    altura: Math.max(360, itens.length * 22 + 80),
    referencia: r.itens.find((i) => i.uf === "BR" && i.produto === produto)?.preco_medio ?? null,
  }
}

export function tabelaRanking(
  r: Ranking, produto: Produto, cab: { estado: string; preco: string; variacao: string; coletas: string },
  fmtPreco: (valor: number) => string, fmtVar: FmtNulo,
): Tabela {
  return {
    colunas: [cab.estado, cab.preco, cab.variacao, cab.coletas],
    linhas: itensRanking(r, produto).map((i) => [i.uf, fmtPreco(i.preco_medio), fmtVar(i.variacao_12m_pct), String(i.n_coletas)]),
  }
}

export function itensRazao(eg: EtanolGasolina): ItemRazao[] {
  return eg.atual.filter((i) => i.uf !== "BR").sort((a, b) => a.razao - b.razao)
}

export function tracosRazaoAtual(eg: EtanolGasolina, nomes: { etanol: string; gasolina: string }): { tracos: Traco[]; altura: number; ordem: string[] } {
  const itens = itensRazao(eg)
  const grupo = (compensa: "etanol" | "gasolina"): Traco => {
    const selecionados = itens.filter((i) => i.compensa === compensa)
    return {
      type: "bar",
      orientation: "h",
      name: nomes[compensa],
      x: selecionados.map((i) => i.razao),
      y: selecionados.map((i) => i.uf),
      marker: { color: CORES_PRODUTO[compensa] },
      hovertemplate: "%{y}: %{x:.1%}<extra>%{fullData.name}</extra>",
    }
  }
  return {
    tracos: [grupo("etanol"), grupo("gasolina")],
    altura: Math.max(360, itens.length * 22 + 100),
    ordem: itens.map((i) => i.uf).reverse(),
  }
}

export function tracosRazaoHistorico(eg: EtanolGasolina, uf: string, nomes: { brasil: string; uf: string }): Traco[] {
  const serie = (regiao: string): Serie => eg.historico.razao[regiao] ?? eg.historico.meses.map(() => null)
  const hover = "%{x|%m/%Y}: %{y:.1%}<extra>%{fullData.name}</extra>"
  const tracos = [linha(eg.historico.meses, serie("BR"), nomes.brasil, CORES_PRODUTO.etanol, 2.5, hover)]
  if (uf !== "BR") tracos.push(linha(eg.historico.meses, serie(uf), nomes.uf, COR_DESTAQUE, 2, hover))
  return tracos
}

export function tabelaRazao(
  eg: EtanolGasolina, cab: { estado: string; razao: string; compensa: string },
  fmtRazao: (valor: number) => string, rotulos: { etanol: string; gasolina: string },
): Tabela {
  return {
    colunas: [cab.estado, cab.razao, cab.compensa],
    linhas: itensRazao(eg).map((i) => [i.uf, fmtRazao(i.razao), rotulos[i.compensa]]),
  }
}

export function linhaVertical(x: number): Record<string, unknown> {
  return { type: "line", xref: "x", yref: "paper", x0: x, x1: x, y0: 0, y1: 1, line: { color: COR_REFERENCIA, width: 1.5, dash: "dash" } }
}

export function linhaHorizontal(y: number): Record<string, unknown> {
  return { type: "line", xref: "paper", yref: "y", x0: 0, x1: 1, y0: y, y1: y, line: { color: COR_REFERENCIA, width: 1.5, dash: "dash" } }
}
```

- [ ] **Passo 5: Implementar `insights.ts`**

`site/src/lib/insights.ts`:

```ts
import type { EtanolGasolina, Evolucao, ItemRanking, Produto, Ranking } from "../types/dados"
import { itensRanking, itensRazao, serieEvolucao } from "./graficos"

export function insightEvolucao(
  evo: Evolucao, produto: Produto = "gasolina",
): { mesInicial: string; inicial: number; atual: number; variacaoPct: number } | null {
  const serie = serieEvolucao(evo, "BR", produto, "real")
  const primeiro = serie.findIndex((v) => v !== null)
  let ultimo = -1
  for (let i = serie.length - 1; i >= 0; i--) {
    if (serie[i] !== null) {
      ultimo = i
      break
    }
  }
  if (primeiro < 0 || ultimo <= primeiro) return null
  const inicial = serie[primeiro] as number
  const atual = serie[ultimo] as number
  return { mesInicial: evo.meses[primeiro], inicial, atual, variacaoPct: (atual / inicial - 1) * 100 }
}

export function insightRanking(
  r: Ranking, produto: Produto, uf = "DF",
): { maisCara: ItemRanking; maisBarata: ItemRanking; posicao: number; total: number } | null {
  const itens = itensRanking(r, produto)
  if (!itens.length) return null
  return {
    maisCara: itens[0],
    maisBarata: itens[itens.length - 1],
    posicao: itens.findIndex((i) => i.uf === uf) + 1,
    total: itens.length,
  }
}

export function ufsEtanol(eg: EtanolGasolina): string[] {
  return itensRazao(eg).filter((i) => i.compensa === "etanol").map((i) => i.uf)
}
```

- [ ] **Passo 6: Rodar e ver passar**

Rodar: `cd site && npx vitest run tests/graficos.spec.ts`
Esperado: todos passam.

- [ ] **Passo 7: Commit**

```bash
cd site
git add src/lib/chartTheme.ts src/lib/graficos.ts src/lib/insights.ts tests/graficos.spec.ts
git commit -m "feat(site): lógica dos gráficos, tabelas e insights" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 9: Componentes base do dashboard (gráfico, tabela, estados)

**Arquivos:**
- Criar: `site/src/types/plotly.d.ts`
- Criar: `site/src/components/dados/PlotlyChart.vue`, `DataTable.vue`, `EstadoDados.vue`
- Criar: `site/tests/componentesDados.spec.ts`

**Interfaces:**
- Consome: `CONFIG_BASE`, `mesclarLayout` e o tipo `Traco`.
- Produz:
  - `<PlotlyChart :dados="Traco[]" :rotulo="string" :layout? :altura?>`. Importa o Plotly só quando o gráfico fica visível, ou imediatamente quando não existe `IntersectionObserver`, e redesenha quando as props mudam.
  - `<DataTable :colunas :linhas :legenda>`, com um botão que mostra e oculta a tabela.
  - `<EstadoDados :carregando :erro>`, com um slot para o conteúdo.

- [ ] **Passo 1: Escrever o teste que falha**

`site/tests/componentesDados.spec.ts`:

```ts
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
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/componentesDados.spec.ts`
Esperado: FALHA com `Failed to resolve import "../src/components/dados/DataTable.vue"`.

- [ ] **Passo 3: Implementar**

`site/src/types/plotly.d.ts`:

```ts
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
```

`site/src/components/dados/PlotlyChart.vue`:

```vue
<script setup lang="ts">
import type PlotlyTipo from "plotly.js-basic-dist-min"
import { onBeforeUnmount, onMounted, ref, watch } from "vue"
import { CONFIG_BASE, mesclarLayout } from "../../lib/chartTheme"
import type { Traco } from "../../lib/graficos"

const props = withDefaults(
  defineProps<{ dados: Traco[]; rotulo: string; layout?: Record<string, unknown>; altura?: number }>(),
  { layout: () => ({}), altura: 380 },
)

const alvo = ref<HTMLDivElement | null>(null)
let plotly: typeof PlotlyTipo | null = null
let visivel = false
let observador: IntersectionObserver | null = null

async function desenhar(): Promise<void> {
  if (!alvo.value || !visivel) return
  plotly ??= (await import("plotly.js-basic-dist-min")).default
  await plotly.react(alvo.value, props.dados, mesclarLayout(props.layout, props.altura), CONFIG_BASE)
}

onMounted(() => {
  if (!("IntersectionObserver" in window)) {
    visivel = true
    void desenhar()
    return
  }
  observador = new IntersectionObserver(
    (entradas) => {
      if (entradas.some((e) => e.isIntersecting)) {
        visivel = true
        observador?.disconnect()
        void desenhar()
      }
    },
    { rootMargin: "200px" },
  )
  if (alvo.value) observador.observe(alvo.value)
})

watch(() => [props.dados, props.layout, props.altura], () => void desenhar(), { deep: true })

onBeforeUnmount(() => {
  observador?.disconnect()
  if (alvo.value && plotly) plotly.purge(alvo.value)
})
</script>

<template>
  <div ref="alvo" class="grafico" role="img" :aria-label="rotulo" :style="{ minHeight: `${altura}px` }"></div>
</template>

<style scoped>
.grafico { width: 100%; }
</style>
```

`site/src/components/dados/DataTable.vue`:

```vue
<script setup lang="ts">
import { ref } from "vue"
import { useI18n } from "vue-i18n"

defineProps<{ colunas: string[]; linhas: string[][]; legenda: string }>()
const { t } = useI18n()
const aberta = ref(false)
</script>

<template>
  <div class="tabela-dados">
    <button type="button" class="botao botao--secundario" :aria-expanded="aberta" @click="aberta = !aberta">
      {{ aberta ? t("dados.ocultarTabela") : t("dados.verTabela") }}
    </button>
    <div v-if="aberta" class="tabela-dados__rolagem" tabindex="0">
      <table>
        <caption>{{ legenda }}</caption>
        <thead>
          <tr>
            <th v-for="c in colunas" :key="c" scope="col">{{ c }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(linha, i) in linhas" :key="i">
            <td v-for="(valor, j) in linha" :key="j">{{ valor }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.tabela-dados { margin-top: 1rem; }
.tabela-dados__rolagem {
  margin-top: 0.75rem; max-height: 360px; overflow: auto;
  border: 1px solid var(--cor-borda); border-radius: 8px; background: var(--cor-superficie);
}
</style>
```

`site/src/components/dados/EstadoDados.vue`:

```vue
<script setup lang="ts">
import { useI18n } from "vue-i18n"
import { perfil } from "../../content/perfil"

defineProps<{ carregando: boolean; erro: boolean }>()
const { t } = useI18n()
</script>

<template>
  <p v-if="erro" class="estado estado--erro" role="status">
    {{ t("dados.indisponivel") }}
    <a :href="perfil.repoPortfolio" target="_blank" rel="noopener">{{ t("dados.verNoGithub") }}</a>
  </p>
  <p v-else-if="carregando" class="estado" role="status">{{ t("dados.carregando") }}</p>
  <slot v-else />
</template>

<style scoped>
.estado { padding: 2rem; text-align: center; background: var(--cor-superficie); border: 1px dashed var(--cor-borda); border-radius: var(--raio); color: var(--cor-texto-suave); }
</style>
```

- [ ] **Passo 4: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam.

- [ ] **Passo 5: Commit**

```bash
cd site
git add vite.config.ts src/types/plotly.d.ts src/components/dados/PlotlyChart.vue src/components/dados/DataTable.vue src/components/dados/EstadoDados.vue tests/componentesDados.spec.ts
git commit -m "feat(site): gráfico Plotly sob demanda, tabela acessível e estados de carregamento" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 10: Página `/dados-combustiveis`

**Arquivos:**
- Criar: `site/src/components/dados/EvolutionPanel.vue`, `RankingPanel.vue`, `EthanolPanel.vue`, `MethodologySection.vue`
- Modificar (substituir por completo): `site/src/views/FuelDataView.vue`
- Criar: `site/tests/FuelDataView.spec.ts`

**Interfaces:**
- Consome: tudo das Tarefas 3, 8 e 9.
- Produz: a página completa, com as seções `data-testid="analise-evolucao"`, `analise-ranking` e `analise-etanol` e o aviso `data-testid="aviso-desatualizado"`.

- [ ] **Passo 1: Escrever o teste que falha**

`site/tests/FuelDataView.spec.ts`:

```ts
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import etanol from "../src/__fixtures__/etanol_gasolina.json"
import evolucao from "../src/__fixtures__/evolucao.json"
import meta from "../src/__fixtures__/meta.json"
import ranking from "../src/__fixtures__/ranking_uf.json"
import FuelDataView from "../src/views/FuelDataView.vue"
import { montar, simularDados, texto } from "./montar"

const plotly = vi.hoisted(() => ({ react: vi.fn(async () => undefined), purge: vi.fn() }))
vi.mock("plotly.js-basic-dist-min", () => ({ default: plotly }))

const TODOS = { "meta.json": meta, "evolucao.json": evolucao, "ranking_uf.json": ranking, "etanol_gasolina.json": etanol }

describe("FuelDataView", () => {
  beforeEach(() => vi.useFakeTimers({ now: new Date("2026-09-30T12:00:00Z"), toFake: ["Date"] }))
  afterEach(() => vi.useRealTimers())

  it("mostra título, data dos dados e as três análises com insights", async () => {
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    const t = texto(w)
    expect(w.get("h1").text()).toBe("Quanto custa abastecer no Brasil?")
    expect(t).toContain("Dados até a semana de 21/09/2026.")
    expect(w.find("[data-testid='aviso-desatualizado']").exists()).toBe(false)
    expect(t).toContain("custava R$ 6,43 em 06/2026 e custa R$ 6,56 hoje: +2,0%")
    expect(t).toContain("Preço mais alto: AC (R$ 7,45)")
    expect(t).toContain("O DF é o 2º mais caro entre 3 estados")
    expect(t).toContain("O etanol compensa em 2 estados: SP, DF.")
    expect(t).toContain("Metodologia")
    expect(document.title).toBe("Preços dos combustíveis no Brasil — Davi Levy")
    await vi.waitFor(() => expect(plotly.react).toHaveBeenCalled())
  })

  it("avisa quando os dados têm mais de 21 dias", async () => {
    vi.setSystemTime(new Date("2026-11-01T12:00:00Z"))
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    expect(w.get("[data-testid='aviso-desatualizado']").text()).toContain("dados de 21/09")
  })

  it("um arquivo com erro não derruba as outras análises", async () => {
    simularDados({ ...TODOS, "evolucao.json": 500 })
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    expect(texto(w.get("[data-testid='analise-evolucao']"))).toContain("Dados indisponíveis no momento.")
    expect(texto(w.get("[data-testid='analise-ranking']"))).toContain("Preço mais alto")
  })

  it("trocar o combustível no ranking atualiza o insight", async () => {
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis" })
    await w.get("[data-testid='ranking-produto']").setValue("etanol")
    expect(texto(w.get("[data-testid='analise-ranking']"))).toContain("Preço mais alto: AC (R$ 5,40)")
  })

  it("em inglês", async () => {
    simularDados(TODOS)
    const w = await montar(FuelDataView, { rota: "/dados-combustiveis", idioma: "en" })
    expect(w.get("h1").text()).toBe("How much does it cost to fill up in Brazil?")
    expect(texto(w)).toContain("Data up to the week of Sep 21, 2026.")
  })
})
```

- [ ] **Passo 2: Rodar e ver falhar**

Rodar: `cd site && npx vitest run tests/FuelDataView.spec.ts`
Esperado: FALHA. O `h1` não existe no esqueleto.

- [ ] **Passo 3: Implementar os painéis**

`site/src/components/dados/EvolutionPanel.vue`:

```vue
<script setup lang="ts">
import { computed, ref } from "vue"
import { useI18n } from "vue-i18n"
import type { Idioma } from "../../i18n"
import { formatarMes, formatarPct, formatarReais } from "../../lib/format"
import { type Modo, tabelaEvolucao, tracosEvolucao } from "../../lib/graficos"
import { insightEvolucao } from "../../lib/insights"
import type { Evolucao, Produto } from "../../types/dados"
import DataTable from "./DataTable.vue"
import PlotlyChart from "./PlotlyChart.vue"

const props = defineProps<{ evolucao: Evolucao }>()
const { t, locale } = useI18n()
const idioma = computed(() => locale.value as Idioma)
const produtos: Produto[] = ["gasolina", "etanol", "diesel_s10"]
const produto = ref<Produto>("gasolina")
const uf = ref("DF")
const modo = ref<Modo>("real")

const ufs = computed(() => Object.keys(props.evolucao.series).filter((u) => u !== "BR").sort())
const tracos = computed(() =>
  tracosEvolucao(props.evolucao, produto.value, uf.value, modo.value, { brasil: t("dados.brasil"), uf: uf.value }),
)
const layout = computed(() => ({
  xaxis: { type: "date", tickformat: "%m/%Y" },
  yaxis: { tickprefix: "R$ ", tickformat: ".2f" },
  separators: idioma.value === "pt" ? ",." : ".,",
}))
const fmtPreco = (v: number | null) => (v === null ? "—" : formatarReais(v, idioma.value))
const tabela = computed(() =>
  tabelaEvolucao(
    props.evolucao, produto.value, uf.value, modo.value,
    { mes: t("dados.mes"), brasil: t("dados.brasil"), uf: uf.value },
    (m) => formatarMes(m, idioma.value), fmtPreco,
  ),
)
const insight = computed(() => {
  const i = insightEvolucao(props.evolucao)
  if (!i) return null
  return t("dados.insightEvolucao", {
    ref: formatarMes(props.evolucao.ipca_ref, idioma.value),
    mes: formatarMes(i.mesInicial, idioma.value),
    inicial: formatarReais(i.inicial, idioma.value),
    atual: formatarReais(i.atual, idioma.value),
    pct: formatarPct(i.variacaoPct, idioma.value),
  })
})
const rotulo = computed(() => t("dados.graficoEvolucao", { produto: t(`produtos.${produto.value}`), uf: uf.value }))
</script>

<template>
  <div>
    <div class="controles">
      <label>
        {{ t("dados.produto") }}
        <select v-model="produto">
          <option v-for="p in produtos" :key="p" :value="p">{{ t(`produtos.${p}`) }}</option>
        </select>
      </label>
      <label>
        {{ t("dados.estado") }}
        <select v-model="uf">
          <option v-for="u in ufs" :key="u" :value="u">{{ u }}</option>
        </select>
      </label>
      <div class="alternador" role="group" :aria-label="t('dados.modoRotulo')">
        <button type="button" class="botao botao--secundario" :aria-pressed="modo === 'real'" @click="modo = 'real'">
          {{ t("dados.real") }}
        </button>
        <button type="button" class="botao botao--secundario" :aria-pressed="modo === 'nominal'" @click="modo = 'nominal'">
          {{ t("dados.nominal") }}
        </button>
      </div>
    </div>
    <PlotlyChart :dados="tracos" :layout="layout" :rotulo="rotulo" />
    <p v-if="insight" class="insight">{{ insight }}</p>
    <DataTable :colunas="tabela.colunas" :linhas="tabela.linhas" :legenda="rotulo" />
  </div>
</template>

<style scoped>
.alternador { display: flex; gap: 0.5rem; flex-wrap: wrap; }
</style>
```

`site/src/components/dados/RankingPanel.vue`:

```vue
<script setup lang="ts">
import { computed, ref } from "vue"
import { useI18n } from "vue-i18n"
import type { Idioma } from "../../i18n"
import { formatarPct, formatarReais } from "../../lib/format"
import { linhaVertical, tabelaRanking, tracosRanking } from "../../lib/graficos"
import { insightRanking } from "../../lib/insights"
import type { Produto, Ranking } from "../../types/dados"
import DataTable from "./DataTable.vue"
import PlotlyChart from "./PlotlyChart.vue"

const props = defineProps<{ ranking: Ranking }>()
const { t, locale } = useI18n()
const idioma = computed(() => locale.value as Idioma)
const produtos: Produto[] = ["gasolina", "etanol", "diesel_s10"]
const produto = ref<Produto>("gasolina")

const fmtVar = (v: number | null) => (v === null ? "—" : formatarPct(v, idioma.value))
const grafico = computed(() => tracosRanking(props.ranking, produto.value, fmtVar))
const layout = computed(() => ({
  xaxis: { tickprefix: "R$ ", tickformat: ".2f", rangemode: "tozero" },
  yaxis: { automargin: true },
  showlegend: false,
  separators: idioma.value === "pt" ? ",." : ".,",
  shapes: grafico.value.referencia === null ? [] : [linhaVertical(grafico.value.referencia)],
}))
const tabela = computed(() =>
  tabelaRanking(
    props.ranking, produto.value,
    { estado: t("dados.estado"), preco: t("dados.preco"), variacao: t("dados.variacao"), coletas: t("dados.coletas") },
    (v) => formatarReais(v, idioma.value), fmtVar,
  ),
)
const insight = computed(() => {
  const i = insightRanking(props.ranking, produto.value)
  if (!i) return null
  return t("dados.insightRanking", {
    caro: i.maisCara.uf,
    precoCaro: formatarReais(i.maisCara.preco_medio, idioma.value),
    barato: i.maisBarata.uf,
    precoBarato: formatarReais(i.maisBarata.preco_medio, idioma.value),
    pos: i.posicao,
    total: i.total,
  })
})
const rotulo = computed(() => t("dados.graficoRanking", { produto: t(`produtos.${produto.value}`) }))
</script>

<template>
  <div>
    <div class="controles">
      <label>
        {{ t("dados.produto") }}
        <select v-model="produto" data-testid="ranking-produto">
          <option v-for="p in produtos" :key="p" :value="p">{{ t(`produtos.${p}`) }}</option>
        </select>
      </label>
    </div>
    <PlotlyChart :dados="grafico.tracos" :layout="layout" :altura="grafico.altura" :rotulo="rotulo" />
    <p v-if="insight" class="insight">{{ insight }}</p>
    <DataTable :colunas="tabela.colunas" :linhas="tabela.linhas" :legenda="rotulo" />
  </div>
</template>
```

`site/src/components/dados/EthanolPanel.vue`:

```vue
<script setup lang="ts">
import { computed, ref } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import type { Idioma } from "../../i18n"
import { formatarRazao } from "../../lib/format"
import { linhaHorizontal, linhaVertical, tabelaRazao, tracosRazaoAtual, tracosRazaoHistorico } from "../../lib/graficos"
import { ufsEtanol } from "../../lib/insights"
import type { EtanolGasolina } from "../../types/dados"
import DataTable from "./DataTable.vue"
import PlotlyChart from "./PlotlyChart.vue"

const props = defineProps<{ etanolGasolina: EtanolGasolina }>()
const { t, locale } = useI18n()
const c = useConteudo()
const idioma = computed(() => locale.value as Idioma)
const separadores = computed(() => (idioma.value === "pt" ? ",." : ".,"))
const uf = ref("DF")
const rotulos = computed(() => ({ etanol: t("dados.compensaEtanol"), gasolina: t("dados.compensaGasolina") }))

const atual = computed(() => tracosRazaoAtual(props.etanolGasolina, rotulos.value))
const layoutAtual = computed(() => ({
  xaxis: { tickformat: ".0%", rangemode: "tozero" },
  yaxis: { automargin: true, categoryorder: "array", categoryarray: atual.value.ordem },
  shapes: [linhaVertical(props.etanolGasolina.limiar)],
  separators: separadores.value,
}))
const ufs = computed(() => Object.keys(props.etanolGasolina.historico.razao).filter((u) => u !== "BR").sort())
const historico = computed(() => tracosRazaoHistorico(props.etanolGasolina, uf.value, { brasil: t("dados.brasil"), uf: uf.value }))
const layoutHistorico = computed(() => ({
  xaxis: { type: "date", tickformat: "%m/%Y" },
  yaxis: { tickformat: ".0%" },
  shapes: [linhaHorizontal(props.etanolGasolina.limiar)],
  separators: separadores.value,
}))
const tabela = computed(() =>
  tabelaRazao(
    props.etanolGasolina,
    { estado: t("dados.estado"), razao: t("dados.razao"), compensa: t("dados.compensa") },
    (v) => formatarRazao(v, idioma.value), rotulos.value,
  ),
)
const insight = computed(() => {
  const lista = ufsEtanol(props.etanolGasolina)
  return lista.length ? t("dados.insightEtanol", { n: lista.length, lista: lista.join(", ") }) : t("dados.insightEtanolNenhum")
})
</script>

<template>
  <div>
    <PlotlyChart :dados="atual.tracos" :layout="layoutAtual" :altura="atual.altura" :rotulo="t('dados.graficoRazao')" />
    <p class="insight">{{ insight }}</p>
    <DataTable :colunas="tabela.colunas" :linhas="tabela.linhas" :legenda="t('dados.graficoRazao')" />
    <h3 class="subtitulo-historico">{{ c.dados.etanol.historicoTitulo }}</h3>
    <div class="controles">
      <label>
        {{ t("dados.estado") }}
        <select v-model="uf">
          <option v-for="u in ufs" :key="u" :value="u">{{ u }}</option>
        </select>
      </label>
    </div>
    <PlotlyChart :dados="historico" :layout="layoutHistorico" :rotulo="t('dados.graficoRazaoHist', { uf })" />
  </div>
</template>

<style scoped>
.subtitulo-historico { margin-top: 2.5rem; }
</style>
```

`site/src/components/dados/MethodologySection.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { perfil } from "../../content/perfil"
import type { Idioma } from "../../i18n"
import { formatarMes, formatarNumero } from "../../lib/format"
import type { Meta } from "../../types/dados"

const props = defineProps<{ meta: Meta | null }>()
const { t, locale } = useI18n()
const c = useConteudo()
const idioma = computed(() => locale.value as Idioma)
const total = computed(() => (props.meta ? formatarNumero(props.meta.n_coletas_total, idioma.value) : null))
</script>

<template>
  <section class="analise" aria-labelledby="metodologia-titulo">
    <h2 id="metodologia-titulo">{{ c.dados.metodologia.titulo }}</h2>
    <ul class="metodologia">
      <li v-for="(item, i) in c.dados.metodologia.itens" :key="i">{{ item }}</li>
    </ul>
    <template v-if="meta">
      <p v-if="total" class="suave">{{ t("dados.totalColetas", { n: total }) }}</p>
      <p v-if="meta.ipca_em_cache" class="suave">{{ t("dados.ipcaCache", { mes: formatarMes(meta.ipca_ate, idioma) }) }}</p>
      <h3>{{ t("dados.fontes") }}</h3>
      <ul>
        <li v-for="f in meta.fontes" :key="f.url">
          <a :href="f.url" target="_blank" rel="noopener">{{ f.nome }}</a>
        </li>
      </ul>
    </template>
    <p>
      <a class="botao botao--secundario" :href="perfil.codigoPipeline" target="_blank" rel="noopener">{{ t("dados.verCodigo") }}</a>
    </p>
  </section>
</template>

<style scoped>
.metodologia { padding-left: 1.1rem; display: grid; gap: 0.5rem; max-width: 75ch; }
</style>
```

- [ ] **Passo 4: Implementar a view**

`site/src/views/FuelDataView.vue` (substituir o esqueleto):

```vue
<script setup lang="ts">
import { computed, watchEffect } from "vue"
import { useI18n } from "vue-i18n"
import EstadoDados from "../components/dados/EstadoDados.vue"
import EthanolPanel from "../components/dados/EthanolPanel.vue"
import EvolutionPanel from "../components/dados/EvolutionPanel.vue"
import MethodologySection from "../components/dados/MethodologySection.vue"
import RankingPanel from "../components/dados/RankingPanel.vue"
import { useConteudo } from "../composables/useConteudo"
import { useFuelData } from "../composables/useFuelData"
import type { Idioma } from "../i18n"
import { formatarData, formatarDiaMes } from "../lib/format"
import { aplicarMeta } from "../lib/seo"
import { dadosDesatualizados } from "../lib/stale"
import type { EtanolGasolina, Evolucao, Meta, Ranking } from "../types/dados"

const { t, locale } = useI18n()
const c = useConteudo()
const idioma = computed(() => locale.value as Idioma)

const { dados: meta, carregando: carregandoMeta } = useFuelData<Meta>("meta.json")
const { dados: evolucao, erro: erroEvolucao, carregando: carregandoEvolucao } = useFuelData<Evolucao>("evolucao.json")
const { dados: ranking, erro: erroRanking, carregando: carregandoRanking } = useFuelData<Ranking>("ranking_uf.json")
const { dados: etanol, erro: erroEtanol, carregando: carregandoEtanol } = useFuelData<EtanolGasolina>("etanol_gasolina.json")

// As análises só entram quando os 4 arquivos responderam (com sucesso ou erro). Até lá, um espaço
// da altura da tela evita que o conteúdo "pule" ao chegar (CLS medido pelo Lighthouse).
const pronto = computed(
  () => ![carregandoMeta, carregandoEvolucao, carregandoRanking, carregandoEtanol].some((c) => c.value),
)
const desatualizado = computed(() => meta.value !== null && dadosDesatualizados(meta.value.semana_mais_recente, new Date()))

watchEffect(() =>
  aplicarMeta({ titulo: t("meta.tituloDados"), descricao: t("meta.descricaoDados"), idioma: idioma.value }),
)
</script>

<template>
  <main id="conteudo" class="container pagina-dados">
    <RouterLink to="/" class="voltar">← {{ t("dados.voltar") }}</RouterLink>
    <header class="pagina-dados__cabecalho">
      <h1>{{ c.dados.titulo }}</h1>
      <p class="secao__subtitulo">{{ c.dados.intro }}</p>
      <p class="pagina-dados__atualizacao">
        <template v-if="meta">
          {{ t("dados.dadosAte", { data: formatarData(meta.semana_mais_recente, idioma) }) }}
          <span v-if="desatualizado" class="selo-aviso" data-testid="aviso-desatualizado">
            {{ t("dados.desatualizado", { data: formatarDiaMes(meta.semana_mais_recente, idioma) }) }}
          </span>
        </template>
      </p>
    </header>

    <p v-if="!pronto" class="pagina-dados__carregando" role="status">{{ t("dados.carregando") }}</p>
    <template v-else>
    <section class="analise" aria-labelledby="evolucao-titulo" data-testid="analise-evolucao">
      <h2 id="evolucao-titulo">{{ c.dados.evolucao.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.dados.evolucao.explicacao }}</p>
      <EstadoDados :carregando="carregandoEvolucao" :erro="erroEvolucao">
        <EvolutionPanel v-if="evolucao" :evolucao="evolucao" />
      </EstadoDados>
    </section>

    <section class="analise" aria-labelledby="ranking-titulo" data-testid="analise-ranking">
      <h2 id="ranking-titulo">{{ c.dados.ranking.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.dados.ranking.explicacao }}</p>
      <EstadoDados :carregando="carregandoRanking" :erro="erroRanking">
        <RankingPanel v-if="ranking" :ranking="ranking" />
      </EstadoDados>
    </section>

    <section class="analise" aria-labelledby="etanol-titulo" data-testid="analise-etanol">
      <h2 id="etanol-titulo">{{ c.dados.etanol.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.dados.etanol.explicacao }}</p>
      <EstadoDados :carregando="carregandoEtanol" :erro="erroEtanol">
        <EthanolPanel v-if="etanol" :etanol-gasolina="etanol" />
      </EstadoDados>
    </section>

    <MethodologySection :meta="meta" />
    </template>
  </main>
</template>

<style scoped>
.pagina-dados { padding-block: 2rem 4rem; }
.voltar { display: inline-flex; align-items: center; min-height: 44px; }
.pagina-dados__cabecalho { padding-block: 1.5rem 1rem; }
.pagina-dados__atualizacao { color: var(--cor-texto-suave); font-size: 0.9375rem; min-height: 1.6em; }
.pagina-dados__carregando { min-height: 100vh; padding-top: 2rem; color: var(--cor-texto-suave); }
.selo-aviso {
  display: inline-block; margin-left: 0.5rem; padding: 0.125rem 0.625rem;
  border-radius: 999px; border: 1px solid var(--cor-ambar); color: var(--cor-ambar); font-size: 0.8125rem;
}
.analise { padding-block: 2.5rem; border-top: 1px solid var(--cor-borda); }
:deep(.insight) {
  margin-top: 1rem; padding: 0.875rem 1rem; border-left: 4px solid var(--cor-verde);
  background: var(--cor-superficie); border-radius: 0 8px 8px 0; color: var(--cor-texto-forte);
}
</style>
```

- [ ] **Passo 5: Rodar e ver passar**

Rodar: `cd site && npx vitest run`
Esperado: todos passam.

- [ ] **Passo 6: Conferir no navegador com os dados reais**

Rodar: `cd site && npm run dev` e abrir `http://localhost:5173/dados-combustiveis`.
Esperado:
- Os gráficos aparecem ao rolar a página.
- O seletor de UF e o botão nominal/real mudam o gráfico.
- A linha tracejada aparece em 70% e na média nacional.
- A tabela abre e fecha.
- Em EN, os números mudam de formato.
- Numa janela de 360 px de largura, não há rolagem horizontal.

Encerre com Ctrl+C.

- [ ] **Passo 7: Commit**

```bash
cd site
git add src/components/dados src/views/FuelDataView.vue tests/FuelDataView.spec.ts
git commit -m "feat(site): página de análise dos combustíveis com três análises e metodologia" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 11: Assets de publicação, fallback de rotas e build

**Arquivos:**
- Criar: `site/public/favicon.svg`, `site/public/robots.txt`, `site/public/sitemap.xml`
- Criar: `site/scripts/og-image.mjs`, que gera `site/public/og-image.png`
- Criar: `site/scripts/spa-fallback.mjs`

**Interfaces:**
- Produz, em `dist/`: `404.html` e `dados-combustiveis/index.html`, este último com título, descrição, `og:*` e `canonical` próprios. Assim o GitHub Pages responde com status 200 nessa rota.

- [ ] **Passo 1: Criar o favicon, o `robots.txt` e o sitemap**

`site/public/favicon.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0f172a"/><text x="32" y="42" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="28" font-weight="700" fill="#38bdf8">DL</text></svg>
```

`site/public/robots.txt`:

```text
User-agent: *
Allow: /
Sitemap: https://davi-kl.github.io/sitemap.xml
```

`site/public/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://davi-kl.github.io/</loc></url>
  <url><loc>https://davi-kl.github.io/dados-combustiveis/</loc></url>
</urlset>
```

- [ ] **Passo 2: Gerar a imagem de compartilhamento (Open Graph)**

`site/scripts/og-image.mjs`:

```js
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
```

Rodar: `cd site && npm run og`
Esperado: `gerado: ...public/og-image.png`. Abra o arquivo e confira que o texto aparece legível, sem caracteres trocados.

- [ ] **Passo 3: Criar o fallback de rotas**

`site/scripts/spa-fallback.mjs`:

```js
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
```

- [ ] **Passo 4: Rodar lint, testes e build**

```bash
cd site
npm run lint
npm test
npm run build
ls dist dist/dados-combustiveis
grep -o "<title>[^<]*</title>" dist/dados-combustiveis/index.html
```

Esperado:
- O `lint` termina sem erros e sem avisos.
- Todos os testes passam.
- O `build` termina com `spa-fallback: ... gerados`.
- `dist` contém `index.html`, `404.html`, `assets/`, `data/`, `favicon.svg`, `og-image.png`, `robots.txt` e `sitemap.xml`.
- `dist/dados-combustiveis` contém `index.html`.
- O `grep` mostra `<title>Preços dos combustíveis no Brasil — Davi Levy</title>`.

- [ ] **Passo 5: Conferir o build e medir com o Lighthouse**

```bash
cd site
npm run preview -- --port 4173
```

Deixe o comando rodando e, em outro terminal, rode:

```bash
cd site
npx --yes lighthouse http://localhost:4173/ --only-categories=performance,accessibility,seo --form-factor=mobile --quiet --chrome-flags="--headless=new" --output=json --output-path=./lh-home.json
npx --yes lighthouse http://localhost:4173/dados-combustiveis/ --only-categories=performance,accessibility,seo --form-factor=mobile --quiet --chrome-flags="--headless=new" --output=json --output-path=./lh-dados.json
node -e "for (const f of ['lh-home.json','lh-dados.json']) { const r = require('./' + f); console.log(f, Object.fromEntries(Object.entries(r.categories).map(([k, v]) => [k, Math.round(v.score * 100)]))) }"
rm lh-home.json lh-dados.json
```

Esperado: as duas páginas com `performance`, `accessibility` e `seo` ≥ 90.
- Se o Lighthouse disser que não encontrou o Chrome, instale o Google Chrome ou faça esta medição depois da publicação (Tarefa 13), pelo PageSpeed Insights.
- Se **acessibilidade** ficar abaixo de 90, abra o relatório HTML (troque `--output=json` por `--output=html`) e corrija o item apontado antes de seguir.
- Se **performance** de `/dados-combustiveis/` ficar abaixo de 90, confirme no relatório que o `plotly` aparece só como *chunk* carregado depois da primeira pintura. Se ele estiver no bundle principal, a importação dinâmica em `PlotlyChart.vue` foi quebrada.

Pare o `preview` com Ctrl+C.

- [ ] **Passo 6: Commit**

```bash
cd site
git add public/favicon.svg public/robots.txt public/sitemap.xml public/og-image.png scripts
git commit -m "feat(site): favicon, imagem OG, sitemap e fallback de rotas para o GitHub Pages" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 12: Deploy automático

**Arquivos:**
- Criar: `.github/workflows/deploy.yml`
- Modificar: `.github/workflows/update-data.yml`, acrescentando o job `deploy` no fim

**Interfaces:**
- Consome: a saída `changed` do job `update` (Parte 1, Tarefa 12).
- Produz: um deploy no GitHub Pages disparado por push em `site/**` ou `schemas/**`, por atualização de dados ou manualmente.

- [ ] **Passo 1: Escrever `deploy.yml`**

`.github/workflows/deploy.yml`:

```yaml
name: Publicar site

on:
  push:
    branches: [main]
    paths: ["site/**", "schemas/**", ".github/workflows/deploy.yml"]
  workflow_call:
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: site
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main # quando chamado após o commit de dados, pega o commit novo

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: site/package-lock.json

      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Passo 2: Ligar o deploy à atualização semanal**

No fim de `.github/workflows/update-data.yml`, depois do job `update` e no mesmo nível de indentação, acrescentar:

```yaml
  deploy:
    needs: update
    if: needs.update.outputs.changed == 'true'
    permissions:
      contents: read
      pages: write
      id-token: write
    uses: ./.github/workflows/deploy.yml
```

- [ ] **Passo 3: Validar a sintaxe dos workflows**

```bash
pipeline/.venv/Scripts/actionlint .github/workflows/deploy.yml .github/workflows/update-data.yml
```

Esperado: nenhuma saída. O `actionlint` foi instalado na Parte 1, Tarefa 12.

- [ ] **Passo 4: Commit**

```bash
git add .github/workflows/deploy.yml .github/workflows/update-data.yml
git commit -m "ci: deploy no GitHub Pages (push, dados novos ou manual)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Tarefa 13: Publicação e aceite (com o Davi)

Os passos 1 e 2 são feitos **pelo Davi**, no site do GitHub. O agente para no início desta tarefa e mostra estas instruções.

**Arquivos:** nenhum novo. Apenas `site/public/cv/` e `site/src/content/perfil.ts`, se os CVs já estiverem prontos.

- [ ] **Passo 1 (Davi): Criar o repositório**

Em https://github.com/new, criar o repositório com:
- nome `Davi-KL.github.io`;
- visibilidade **Public**;
- **sem** README, .gitignore ou licença.

- [ ] **Passo 2 (Davi): Ativar o Pages por Actions**

No repositório, abrir **Settings → Pages → Build and deployment → Source** e escolher **GitHub Actions**.

- [ ] **Passo 3: Enviar o código**

```bash
git remote add origin https://github.com/Davi-KL/Davi-KL.github.io.git
git push -u origin main
```

Esperado: na aba **Actions**, o workflow "Publicar site" roda e termina verde. A URL `https://davi-kl.github.io/` abre o portfólio.

- [ ] **Passo 4: Testar o workflow de dados**

Em **Actions → Atualizar dados ANP → Run workflow**, rodar com `mode = update`.
Esperado: termina verde. Se a ANP publicou dados novos desde o backfill, aparece um commit `data: atualização semanal ANP (semana ...)` e o deploy roda em seguida. Se não, o log mostra "Nenhum dado novo.".

- [ ] **Passo 5: Aceite**

Verificar no site publicado:
- `https://davi-kl.github.io/dados-combustiveis/` aberto direto, numa aba nova, carrega a análise e **não** a home. O título da aba é "Preços dos combustíveis no Brasil — Davi Levy".
- O botão PT/EN troca tudo, inclusive os números dos gráficos. Depois de recarregar a página, o idioma escolhido continua.
- No celular, ou com o DevTools a 360 px, não há rolagem horizontal e o menu abre e fecha.
- O PageSpeed Insights (https://pagespeed.web.dev/), no modo mobile, dá ≥ 90 em Performance, Acessibilidade e SEO nas duas URLs.
- Colar o link no WhatsApp ou no LinkedIn mostra a imagem de compartilhamento.

- [ ] **Passo 6 (quando o Davi enviar os CVs): Ativar o botão de CV**

Salvar os PDFs, **sem endereço e sem telefone**, como `site/public/cv/cv-pt.pdf` e `site/public/cv/cv-en.pdf`. Em `site/src/content/perfil.ts`, trocar a linha:

```ts
export const cv: Record<Idioma, string | null> = { pt: null, en: null }
```

por:

```ts
export const cv: Record<Idioma, string | null> = { pt: "/cv/cv-pt.pdf", en: "/cv/cv-en.pdf" }
```

```bash
cd site
npm test
git add public/cv src/content/perfil.ts
git commit -m "feat(site): CV para download em PT e EN" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push
```

Esperado: depois do deploy, os botões "Baixar CV" aparecem no hero e no contato.
