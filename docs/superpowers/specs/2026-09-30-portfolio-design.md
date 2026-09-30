# Portfólio Davi Levy — Design

**Data:** 2026-09-30
**Status:** aguardando revisão do Davi

## 1. Objetivo e critérios de sucesso

**Objetivo:** um site de portfólio que apresente as experiências e os projetos do Davi de forma clara e visualmente apresentável, e que prove sua capacidade de coletar, tratar, analisar e visualizar dados, usando o Levantamento de Preços de Combustíveis da ANP.

**Público:** recrutadores e líderes técnicos de vagas 100% remotas em desenvolvimento web, back-end, full stack ou análise de dados, no Brasil e no exterior.

**Critérios de sucesso:**
- Um recrutador entende em menos de 1 minuto quem é o Davi, o que ele fez e como contatá-lo.
- A análise da ANP mostra, com código aberto e gráficos, o ciclo completo: coleta, limpeza, agregação, análise, visualização e automação.
- Os dados se atualizam sozinhos toda semana, sem intervenção manual.
- Nota ≥ 90 no Lighthouse (Performance, Acessibilidade e SEO) nas duas rotas.

## 2. Decisões tomadas

| Tema | Decisão |
|---|---|
| Análise de dados | Pipeline Python + dashboard interativo + atualização semanal por GitHub Actions |
| Tecnologia do site | Vue 3 + Vite, vue-router, vue-i18n, Plotly.js |
| Estética | "Data-forward": azul-marinho escuro, números e gráficos em destaque |
| Estrutura | Home (`/`) + página própria `/dados-combustiveis` |
| Idiomas | Português e inglês, com botão PT/EN; idioma inicial segue o navegador |
| Contato | Só links (e-mail, LinkedIn, GitHub) + CV em PDF sem endereço e telefone |
| Arquitetura | Um repositório, com `pipeline/` e `site/` comunicando-se apenas por arquivos JSON |
| Análises | (1) evolução dos preços, (2) comparação entre UFs, (3) etanol × gasolina |
| Inflação | Botão nominal/corrigido pelo IPCA no gráfico de evolução |
| Hospedagem | GitHub Pages, no repositório `Davi-KL.github.io` (URL `https://davi-kl.github.io/`) |

## 3. Arquitetura

```
.
├── pipeline/                 Python 3.11 · Pandas · requests · jsonschema · pytest
│   ├── src/anp/
│   │   ├── collect.py        download com cache e novas tentativas
│   │   ├── clean.py          padronização de colunas, produtos, datas e preços
│   │   ├── aggregate.py      médias semanais por UF × produto
│   │   ├── merge.py          upsert na base histórica
│   │   ├── ipca.py           série IPCA (BCB SGS 433) + índice acumulado
│   │   ├── export.py         gera os JSONs do site
│   │   ├── validate.py       checagens de sanidade antes de exportar
│   │   └── cli.py            comandos `backfill` e `update`
│   ├── data/
│   │   ├── raw/              downloads (fora do git)
│   │   └── processed/        semanal_uf.csv, ipca.csv (versionados)
│   └── tests/                fixtures CSV pequenas, sem rede
├── schemas/                  JSON Schema de cada arquivo exportado (contrato)
├── site/                     Vue 3 · Vite · vue-router · vue-i18n · Plotly.js · Vitest
│   ├── src/content/          pt.json, en.json (textos, projetos, experiência)
│   ├── src/views/            HomeView.vue, FuelDataView.vue
│   ├── src/components/       seções da home, cards, gráficos
│   ├── src/composables/      useFuelData (carregamento + estados de erro)
│   └── public/
│       ├── data/             JSONs gerados pelo pipeline
│       └── cv/               cv-pt.pdf, cv-en.pdf
└── .github/workflows/        update-data.yml, deploy.yml
```

**Regra de fronteira:** o pipeline não conhece o Vue e o site não conhece o Pandas. A única interface entre eles são os arquivos em `site/public/data/`, cujo formato é definido por `schemas/`.

## 4. Pipeline de dados

### 4.1 Fontes

Página oficial: https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/serie-historica-de-precos-de-combustiveis

| Conjunto | Cobertura (em 30/09/2026) | Padrão de URL | Uso |
|---|---|---|---|
| Semestral, combustíveis automotivos | 2004-S1 a 2026-S1 | `.../arquivos/shpc/dsas/ca/ca-AAAA-SS.zip` | carga histórica |
| Mensal, gasolina + etanol | 2023-01 a 2026-08 | `.../arquivos/shpc/dsan/AAAA/MM-dados-abertos-precos-AAAA-MM-gasolina-etanol.csv` | lacuna entre o último semestre e hoje |
| Mensal, diesel + GNV | 2023-01 a 2026-08 | `.../arquivos/shpc/dsan/AAAA/MM-dados-abertos-precos-AAAA-MM-diesel-gnv.csv` | idem |
| Últimas 4 semanas | atualizado semanalmente | `.../arquivos/shpc/qus/ultimas-4-semanas-<produto>.csv` | atualização semanal |
| IPCA mensal (BCB SGS 433) | 1980 → hoje | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json` | correção pela inflação |

Os nomes exatos dos arquivos das "últimas 4 semanas" e o esquema de colunas de cada época são confirmados na primeira tarefa do plano, contra a página da ANP e o [PDF de metadados](https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/metadados-serie-historica-precos-combustiveis.pdf).

### 4.2 Escopo

- **Produtos:** gasolina comum, etanol hidratado e diesel S10. Ficam de fora a gasolina aditivada, o GNV, o GLP e o diesel comum/S500.
- **Período:** de 2004 até hoje para gasolina e etanol. O diesel S10 começa em 2013, quando o produto passou a ser pesquisado; a metodologia explica isso.
- **Granularidade publicada:** médias por UF (27) e Brasil.

### 4.3 Etapas

1. **Coletar.** Baixa os arquivos para `data/raw/`, com cache pelo nome do arquivo, timeout de 60 s e 3 tentativas com espera crescente.
2. **Limpar.**
   - Mapeia as variações de nome de coluna para um esquema canônico: `data_coleta`, `uf`, `municipio`, `produto`, `preco_venda`, `bandeira`.
   - Converte datas `dd/mm/aaaa` e decimais com vírgula.
   - Normaliza o nome do produto para `gasolina`, `etanol` ou `diesel_s10` e descarta os demais.
   - Remove duplicatas e preços fora da faixa plausível de R$ 0,50 a R$ 20,00 por litro.
   - Se faltar uma coluna obrigatória, falha com uma mensagem que lista as colunas encontradas e as esperadas.
3. **Agregar.** Por semana ISO (identificada pela segunda-feira), UF e produto, calcula `preco_medio`, `preco_mediano` e `n_coletas`. A linha `BR` é calculada sobre todas as coletas do país, e não como média das médias estaduais.
4. **Mesclar.** Faz upsert em `processed/semanal_uf.csv` pela chave (`semana`, `uf`, `produto`). As semanas presentes na entrada nova sempre sobrescrevem as antigas, para absorver revisões da ANP. A operação é idempotente.
5. **IPCA.** Baixa a série 433 e monta um índice acumulado mensal em `processed/ipca.csv`. O preço real é `nominal × (índice_ref / índice_mês)`, em que `índice_ref` é o último mês com IPCA publicado.
6. **Validar.** Veja a seção 6.
7. **Exportar.** Grava os quatro JSONs da seção 4.4 e valida cada um contra `schemas/`.

**`backfill`** (roda uma vez, localmente) processa um arquivo semestral por vez, agrega e descarta o bruto da memória. Em seguida processa os mensais posteriores ao último semestre e, por fim, as últimas 4 semanas.
**`update`** (roda semanalmente) processa só as "últimas 4 semanas" e o IPCA.

### 4.4 Arquivos exportados (contrato)

Todos ficam em `site/public/data/` e usam formato colunar para ficarem pequenos.

**`evolucao.json`**: análise 1

```json
{
  "meses": ["2004-05", "..."],
  "ipca_ref": "2026-08",
  "series": {
    "BR": { "gasolina": { "nominal": [2.05, "..."], "real": [6.10, "..."] },
            "etanol": { "...": "..." }, "diesel_s10": { "...": "..." } },
    "DF": { "...": "..." }
  }
}
```

A média mensal é a média das médias semanais do mês. Meses sem dado ficam `null`.

**`ranking_uf.json`**: análise 2

```json
{
  "periodo": { "inicio": "2026-09-01", "fim": "2026-09-22" },
  "itens": [ { "uf": "DF", "produto": "gasolina", "preco_medio": 6.21,
               "variacao_12m_pct": 3.4, "n_coletas": 812 } ]
}
```

O `preco_medio` é a média das últimas 4 semanas. A `variacao_12m_pct` compara esse valor com as mesmas 4 semanas de um ano antes.

**`etanol_gasolina.json`**: análise 3

```json
{
  "limiar": 0.70,
  "atual": [ { "uf": "SP", "razao": 0.66, "compensa": "etanol" } ],
  "historico": { "meses": ["2004-05", "..."], "razao": { "BR": ["..."], "DF": ["..."] } }
}
```

A razão é `preço etanol / preço gasolina`. Se `razao < limiar`, `compensa = "etanol"`; caso contrário, `"gasolina"`.

**`meta.json`**: rodapé do dashboard e home

```json
{
  "atualizado_em": "2026-10-03T12:04:00Z",
  "semana_mais_recente": "2026-09-22",
  "n_coletas_total": 21000000,
  "ipca_ate": "2026-08",
  "ipca_em_cache": false,
  "fontes": [ { "nome": "ANP", "url": "..." }, { "nome": "BCB SGS 433", "url": "..." } ],
  "destaques": {
    "gasolina_df": 6.21, "gasolina_br": 6.05, "diff_df_br_pct": 2.6,
    "ufs_etanol_compensa": 9,
    "maior_alta_12m": { "uf": "AC", "produto": "diesel_s10", "pct": 8.1 }
  },
  "serie_home": { "meses": ["2024-09", "..."], "gasolina_br": ["..."], "gasolina_df": ["..."] }
}
```

`serie_home` guarda os últimos 24 meses, para a home desenhar o minigráfico sem carregar `evolucao.json`.

## 5. Site

### 5.1 Home (`/`)

1. **Hero.**
   - Nome, "Desenvolvedor Full Stack · Dados" e a frase "Código que resolve. Dados que explicam." / "Code that solves. Data that explains.".
   - Três números em destaque: "2+ anos em health tech", "6 projetos em destaque" e "Gasolina no DF: R$ X,XX". O último vem de `meta.json` e some se o arquivo falhar.
   - Botões: Ver projetos · Baixar CV · GitHub · LinkedIn.
2. **Sobre + Stack.**
   - Resumo curto.
   - Stack agrupada:
     - **Front-end:** HTML5, CSS3, JavaScript, TypeScript, React, Angular, Vue.js, Quasar.
     - **Back-end:** C#, ASP.NET MVC, .NET Core/Framework, Python, Django, Node/Express, SQL, PostgreSQL, PL/SQL, SQLite.
     - **Dados/IA:** Pandas, NumPy, Scikit-learn, Matplotlib, Plotly, Seaborn.
     - **DevOps:** Docker, Git, GitHub Actions, Azure DevOps, Linux, Electron.
   - Formação: UniCEUB, Ciência da Computação (2025–2027), e UnB, Engenharia de Software (2022–2024).
   - Certificações: Google AI Essentials e Google AI Professional Certificate.
   - Idiomas: português nativo e inglês fluente.
3. **Experiência** em linha do tempo.
   - **Destaque:** Rede SARAH (Associação das Pioneiras Sociais), Estagiário de TI e Desenvolvedor de Sistemas Web, jan/2024–jan/2026. Traz os 5 itens do currículo: PL/SQL em larga escala sob LGPD, desenvolvimento web interno, modernização de sistema legado, testes, suporte e infraestrutura. É só texto, sem prints nem código, por se tratar de sistemas internos com dados sensíveis.
   - **"Outras experiências", em formato compacto:** Zenit Aerospace, Assessor Comercial (2023–2024), e Sabin Medicina Diagnóstica, Jovem Aprendiz (2021–2022).
4. **Projetos**: 6 cards. Cada um tem título, descrição de 1 a 2 frases, "Meu papel", tecnologias e links.

| Projeto | Resumo | Meu papel | Links |
|---|---|---|---|
| **NODUS** | App desktop Windows para psicólogos clínicos: prontuários, agenda e histórico de pacientes. Angular + Express local + SQLite empacotados com Electron, 100% offline e com AES-256 (chave derivada da senha, só em memória). Segue a LGPD e a Resolução CFP 06/2019. Projeto Integrador II do CEUB, com Catharina e Miguel. | Gerente de projeto, Scrum Master, back-end e DevOps | `cathsatile/NODUS-Projeto-Integrador-II`, `Davi-KL/NODUS-Projeto-Integrador-II` |
| **ForUnB** | Fórum de perguntas e respostas open-source para mentoria entre estudantes da UnB (Django, Docker). | Back-end, testes e DevOps: automação de CI/CD e deploy | `Davi-KL/2024-1-forUnB` |
| **SOMA** | Análise do uso excessivo de redes sociais e da saúde mental, com dashboard interativo (Python, Pandas, Matplotlib, HTML/CSS/JS). | Front-end, criação dos gráficos e análise dos dados coletados pela Catharina | `cathsatile/SOMA_Social-Media-Overuse-And-Mental-Assessment_` |
| **Análise ANP** | O pipeline e o dashboard deste portfólio, com atualização semanal automática. | Projeto individual: todo o ciclo | este repositório + `/dados-combustiveis` |
| **FlowPad** | App em segundo plano para capturar ideias em menos de 3 s (`Ctrl+Shift+Space`). Tem 5 tipos de entrada, lembretes, dashboard com busca e armazenamento local em JSON. Python 3.11, multiplataforma, testes com pytest, `.exe` nas Releases, licença MIT. | Projeto individual | `Davi-KL/FlowPad` |
| **Projeto Compiladores** | Compilador em C. A descrição de 1 a 2 frases é escrita a partir do README do repositório durante a implementação e aprovada pelo Davi. | a confirmar com o Davi durante a implementação | `Davi-KL/Projeto-Compiladores` |

   No fim da seção, o link "Ver todos no GitHub" aponta para `github.com/Davi-KL?tab=repositories`.

5. **Prévia da análise ANP.**
   - Minigráfico em SVG próprio, sem Plotly, com a gasolina no Brasil e no DF nos últimos 24 meses (`meta.serie_home`).
   - Três insights de `meta.destaques`, com os textos definidos nos arquivos de i18n:
     - DF em relação ao Brasil;
     - número de UFs onde o etanol compensa;
     - maior alta em 12 meses.
   - Botão "Ver análise completa →".
6. **Contato.** Links para daviklevy@gmail.com (mailto), linkedin.com/in/davi-levy-dev e github.com/Davi-KL, mais o botão "Baixar CV", que entrega `cv-pt.pdf` ou `cv-en.pdf` conforme o idioma ativo.

### 5.2 `/dados-combustiveis`

- **Cabeçalho:** a pergunta que guia a análise, a fonte (ANP e BCB) e "dados até a semana de DD/MM/AAAA".
- **Análise 1, evolução:** gráfico de linhas mensal. Mostra Brasil e DF por padrão, com seletor de UF, seletor de produto e botão nominal/real (IPCA).
- **Análise 2, estados:** barras horizontais ordenadas pelo preço médio das últimas 4 semanas, com seletor de produto, DF em destaque e a variação em 12 meses no tooltip.
- **Análise 3, etanol × gasolina:** barras da razão por UF com uma linha de referência em 0,70. As cores indicam "compensa etanol" ou "compensa gasolina". Abaixo, um gráfico de linha da razão ao longo do tempo para a UF selecionada.
- Cada análise tem um parágrafo "o que isso mostra", o insight principal e o botão "ver dados em tabela".
- **Metodologia:** fontes, limpeza, faixa plausível, diesel S10 a partir de 2013, média nacional sobre todas as coletas, correção pelo IPCA e link para `pipeline/` no GitHub.
- O Plotly.js (bundle parcial, só com os tipos de gráfico usados) é carregado apenas nesta rota, via import dinâmico.

### 5.3 Visual

- **Tokens de cor:** fundo `#0f172a`, superfície `#1e293b`, texto `#e2e8f0` e texto secundário `#94a3b8`. Destaques em `#38bdf8` (azul), `#a78bfa` (violeta) e `#34d399` (verde).
- **Cor fixa por produto** em todos os gráficos. As cores exatas são validadas quanto a contraste no plano.
- Fonte Inter. Tema só escuro.
- Layout mobile-first, sem rolagem horizontal a partir de 360 px.
- Contraste WCAG AA, foco visível e navegação completa pelo teclado.
- Tags `<title>`, `description` e Open Graph por rota e por idioma, com uma imagem OG.

### 5.4 Roteamento no GitHub Pages

O site usa `createWebHistory` para as URLs ficarem limpas. O build copia `index.html` para `404.html`, então abrir `/dados-combustiveis` direto funciona. O `base` do Vite é `/`, já que o repositório `Davi-KL.github.io` publica na raiz.

## 6. Automação e tratamento de erros

### 6.1 Workflows

- **`update-data.yml`:**
  - Disparo por cron `0 12 * * 6` (sábado, 9h em Brasília) e por `workflow_dispatch`. O disparo manual aceita o parâmetro `mode` com os valores `update` (padrão) ou `backfill`.
  - Passos: instala Python → pytest → `anp update` → valida → commit feito pelo `github-actions[bot]`, só se houver diferença, com a mensagem `data: atualização semanal ANP (semana AAAA-MM-DD)` → chama `deploy.yml` via `workflow_call`.
- **`deploy.yml`:**
  - Disparo por push em `main` que altere `site/**` ou `schemas/**`, por `workflow_call` e por `workflow_dispatch`.
  - Passos: `npm ci` → lint → Vitest → `vite build` → cópia do `404.html` → `actions/deploy-pages`.

### 6.2 Princípio

Dado inválido nunca é publicado. Qualquer falha do pipeline encerra o job **sem commit**, o site continua com a última versão boa e o GitHub notifica o Davi por e-mail.

| Falha | Comportamento |
|---|---|
| ANP indisponível ou URL alterada | 3 tentativas com espera crescente; depois, falha |
| Coluna obrigatória ausente | Falha, listando as colunas encontradas e as esperadas |
| Checagem de sanidade (`validate.py`) | Falha se houver preço fora da faixa, se faltar alguma das 27 UFs na semana mais recente, se a média nacional variar 25% ou mais entre semanas consecutivas, se houver data futura ou se a semana mais recente for anterior à que já está na base |
| API do BCB indisponível | Usa `processed/ipca.csv`, corrige até o último mês disponível e grava `ipca_em_cache: true` no `meta.json` |
| Site: um JSON falha ao carregar | O card mostra "Dados indisponíveis no momento" e um link para o GitHub. Na home, a prévia ANP e o número de gasolina no hero ficam ocultos |
| Site: `semana_mais_recente` com mais de 21 dias | Aviso "dados de DD/MM" no cabeçalho do dashboard |

## 7. Testes

- **Pipeline (pytest, sem rede, com HTTP simulado):**
  - `clean` com fixtures que imitam os formatos de 2004, de cerca de 2015 e o atual;
  - `aggregate` com médias calculadas à mão;
  - `merge` idempotente: aplicar a mesma entrada duas vezes gera a mesma base;
  - sobrescrita de semanas revisadas;
  - `ipca` com índice e deflação calculados à mão;
  - `validate` cobrindo cada regra;
  - `export` validado contra `schemas/`.
- **Contrato:** os JSONs de exemplo usados nos testes do site ficam em `site/src/__fixtures__/` e também são validados contra `schemas/`.
- **Site (Vitest + Vue Test Utils):**
  - `pt.json` e `en.json` com o mesmo conjunto de chaves;
  - `useFuelData` nos estados sucesso, erro e dados antigos;
  - formatação de moeda e data em pt-BR e en;
  - cálculo do minigráfico;
  - renderização básica de cada seção e de cada gráfico.
- **Aceite antes de publicar:** Lighthouse ≥ 90 em Performance, Acessibilidade e SEO nas duas rotas, no modo mobile.

## 8. Pendências do Davi antes de publicar

1. Fornecer `cv-pt.pdf` e `cv-en.pdf` sem endereço e telefone. Sem esses arquivos, o botão "Baixar CV" não aparece.
2. Aprovar a descrição e o "Meu papel" do Projeto Compiladores.
3. Criar o repositório `Davi-KL.github.io` e ativar o GitHub Pages com a origem "GitHub Actions".
4. Recomendado: atualizar a descrição do NODUS no currículo e no LinkedIn (hoje diz "Capacitor, IndexedDB").

## 9. Fora do escopo (v1)

- Análises de bandeiras e postos e de bairros do DF.
- GNV, GLP e gasolina aditivada.
- Mapa coroplético, tema claro, formulário de contato e blog.
