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
