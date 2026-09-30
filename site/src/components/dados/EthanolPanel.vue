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
