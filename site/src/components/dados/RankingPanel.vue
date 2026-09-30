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
