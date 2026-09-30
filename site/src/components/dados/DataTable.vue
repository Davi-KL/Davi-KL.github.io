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
