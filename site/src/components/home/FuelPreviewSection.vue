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
const cores = ["ambar", "verde", "ciano"]

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
      <div class="previa__texto">
        <h2 id="previa-titulo">{{ c.previa.titulo }}</h2>
        <p class="previa__proposito">{{ c.previa.proposito }}</p>
        <p class="secao__subtitulo">{{ c.previa.subtitulo }}</p>
        <ul class="previa__insights">
          <li v-for="(insight, k) in insights" :key="k">
            <span :class="['chip', `chip--${cores[k % cores.length]}`]">{{ insight }}</span>
          </li>
        </ul>
        <RouterLink class="botao" to="/dados-combustiveis">{{ t("previa.verAnalise") }}</RouterLink>
      </div>
      <figure v-if="caminhos" class="previa__painel">
        <svg :viewBox="`0 0 ${LARGURA} ${ALTURA}`" role="img" :aria-label="t('previa.graficoRotulo')" preserveAspectRatio="none">
          <path :d="caminhos.br" fill="none" stroke="var(--cor-destaque)" stroke-width="2.5" vector-effect="non-scaling-stroke" />
          <path :d="caminhos.df" fill="none" stroke="var(--cor-ciano)" stroke-width="2" vector-effect="non-scaling-stroke" />
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
.previa { display: grid; grid-template-columns: minmax(0, 1fr); gap: 2.5rem; align-items: center; }
@media (min-width: 900px) { .previa { grid-template-columns: 1.1fr 0.9fr; gap: 3.5rem; } }
.previa h2 { margin-bottom: 1rem; }
.previa__proposito { color: var(--cor-texto); margin-bottom: 0.75rem; max-width: 60ch; }
.previa__insights { list-style: none; padding: 0; display: grid; gap: 0.6rem; margin: 1.5rem 0 2rem; }
.previa__insights .chip { font-size: 0.9375rem; padding: 0.55rem 1rem; line-height: 1.4; }

.previa__painel {
  margin: 0; padding: clamp(1.25rem, 3vw, 2rem);
  background: var(--cor-superficie); border: 1px solid var(--cor-borda);
  border-radius: var(--raio-grande);
}
.previa__painel svg { width: 100%; height: 160px; }
.previa__legenda { display: flex; align-items: center; gap: 0.5rem; font-size: 0.9rem; color: var(--cor-texto-suave); margin-top: 1rem; }
.chave { display: inline-block; width: 18px; height: 3px; border-radius: 2px; }
.chave--br { background: var(--cor-destaque); }
.chave--df { background: var(--cor-ciano); margin-left: 0.9rem; }
</style>
