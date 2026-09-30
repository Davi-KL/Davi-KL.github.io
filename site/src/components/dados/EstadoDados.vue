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
/* min-height perto da altura padrão de um PlotlyChart (380px): evita que a seção "pule"
   quando o texto de carregando/erro vira o gráfico de verdade (CLS), já que agora cada
   seção aparece assim que os próprios dados chegam, sem esperar as outras. */
.estado {
  min-height: 380px; display: flex; align-items: center; justify-content: center;
  padding: 2rem; text-align: center; background: var(--cor-superficie);
  border: 1px dashed var(--cor-borda); border-radius: var(--raio); color: var(--cor-texto-suave);
}
</style>
