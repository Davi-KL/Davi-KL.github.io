<script setup lang="ts">
import SiteFooter from "./components/layout/SiteFooter.vue"
import SiteHeader from "./components/layout/SiteHeader.vue"
</script>

<template>
  <SiteHeader />
  <!-- altura mínima: enquanto a rota carregada sob demanda chega, o rodapé fica fora da tela e não "pula" (CLS) -->
  <div class="app__rota">
    <RouterView />
  </div>
  <SiteFooter />
</template>

<style scoped>
.app__rota { min-height: 100vh; }
</style>
