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
        <p class="previa__proposito">{{ c.previa.proposito }}</p>
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
.previa__proposito { color: var(--cor-texto); margin-bottom: 0.5rem; }
.previa__insights { padding-left: 1.1rem; display: grid; gap: 0.5rem; margin: 0 0 1.5rem; }
.previa__grafico { margin: 0; }
.previa__grafico svg { width: 100%; height: 140px; }
.previa__legenda { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--cor-texto-suave); margin-top: 0.75rem; }
.chave { display: inline-block; width: 16px; height: 3px; border-radius: 2px; }
.chave--br { background: var(--cor-azul); }
.chave--df { background: var(--cor-ambar); margin-left: 0.75rem; }
</style>
