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
.estado { padding: 2rem; text-align: center; background: var(--cor-superficie); border: 1px dashed var(--cor-borda); border-radius: var(--raio); color: var(--cor-texto-suave); }
</style>
