<script setup lang="ts">
import { ref } from "vue"
import { useI18n } from "vue-i18n"

defineProps<{ colunas: string[]; linhas: string[][]; legenda: string; }>()
const { t } = useI18n()
const aberta = ref(false)

// Uma cor por coluna, na ordem das cores de destaque da página.
const CLASSES = ["col--texto", "col--ambar", "col--verde", "col--ciano"]
const colClasse = (j: number): string => CLASSES[j % CLASSES.length]
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
            <th v-for="(c, j) in colunas" :key="c" scope="col" :class="colClasse(j)">{{ c }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(linha, i) in linhas" :key="i">
            <td v-for="(valor, j) in linha" :key="j" :class="colClasse(j)">{{ valor }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.tabela-dados { margin-top: 1rem; }
.col--texto { color: var(--cor-texto-forte); }
.col--ambar { color: var(--cor-destaque); }
.col--verde { color: var(--cor-verde); }
.col--ciano { color: var(--cor-ciano); }
th[class^="col--"] { border-bottom: 2px solid currentColor; }
td[class^="col--"] { font-variant-numeric: tabular-nums; }
tbody tr.linha--destaque td { background: color-mix(in srgb, var(--cor-destaque) 14%, transparent); font-weight: 650; }
tbody tr.linha--destaque td:first-child { box-shadow: inset 3px 0 0 var(--cor-destaque); }
tbody tr:nth-child(even):not(.linha--destaque) td { background: color-mix(in srgb, var(--cor-texto-forte) 4%, transparent); }
.tabela-dados__rolagem {
  margin-top: 0.75rem; max-height: 360px; overflow: auto;
  border: 1px solid var(--cor-borda); border-radius: 8px; background: var(--cor-superficie);
}
</style>
