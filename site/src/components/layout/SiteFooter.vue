<script setup lang="ts">
import { useI18n } from "vue-i18n"
import { perfil } from "../../content/perfil"

const { t } = useI18n()
const ano = new Date().getFullYear()
</script>

<template>
  <footer class="rodape">
    <div class="container rodape__conteudo">
      <p>© {{ ano }} Davi Levy · {{ t("rodape.texto") }}</p>
      <a :href="perfil.repoPortfolio" target="_blank" rel="noopener">{{ t("rodape.codigo") }}</a>
    </div>
  </footer>
</template>

<style scoped>
.rodape { border-top: 1px solid var(--cor-borda); padding-block: 2rem; color: var(--cor-texto-suave); font-size: 0.875rem; }
.rodape__conteudo { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 0.5rem 1.5rem; }
.rodape p { margin: 0; }
</style>
