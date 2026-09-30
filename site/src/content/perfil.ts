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
