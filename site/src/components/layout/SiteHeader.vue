<script setup lang="ts">
import { ref } from "vue"
import { useI18n } from "vue-i18n"
import { definirIdioma } from "../../i18n"

const { t, locale } = useI18n()
const menuAberto = ref(false)
const ancoras = ["sobre", "experiencia", "projetos"] as const

function alternarIdioma(): void {
  definirIdioma(locale.value === "pt" ? "en" : "pt")
}
</script>

<template>
  <a class="pular" href="#conteudo">{{ t("nav.pularConteudo") }}</a>
  <header class="cabecalho">
    <div class="container cabecalho__barra">
      <RouterLink to="/" class="cabecalho__marca">Davi Levy</RouterLink>
      <button
        type="button"
        class="cabecalho__menu botao botao--secundario"
        data-testid="menu"
        :aria-expanded="menuAberto"
        aria-controls="nav-principal"
        @click="menuAberto = !menuAberto"
      >
        {{ t("nav.menu") }}
      </button>
      <nav id="nav-principal" class="cabecalho__nav" :class="{ 'cabecalho__nav--aberta': menuAberto }" :aria-label="t('nav.rotulo')">
        <RouterLink v-for="a in ancoras" :key="a" :to="{ path: '/', hash: `#${a}` }" @click="menuAberto = false">
          {{ t(`nav.${a}`) }}
        </RouterLink>
        <RouterLink to="/dados-combustiveis" @click="menuAberto = false">{{ t("nav.dados") }}</RouterLink>
        <RouterLink :to="{ path: '/', hash: '#contato' }" @click="menuAberto = false">{{ t("nav.contato") }}</RouterLink>
      </nav>
      <button
        type="button"
        class="cabecalho__idioma botao botao--secundario"
        data-testid="trocar-idioma"
        :aria-label="t('nav.idiomaRotulo')"
        @click="alternarIdioma"
      >
        {{ t("nav.idiomaCurto") }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.cabecalho {
  position: sticky; top: 0; z-index: 50;
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--cor-borda);
}
.cabecalho__barra { display: flex; align-items: center; gap: 0.75rem; min-height: 64px; flex-wrap: wrap; }
.cabecalho__marca { font-weight: 700; color: var(--cor-texto-forte); text-decoration: none; margin-right: auto; }
.cabecalho__nav { display: none; width: 100%; flex-direction: column; padding-bottom: 0.75rem; order: 3; }
.cabecalho__nav--aberta { display: flex; }
.cabecalho__nav a {
  color: var(--cor-texto); text-decoration: none; padding: 0.625rem 0.25rem;
  min-height: 44px; display: flex; align-items: center;
}
.cabecalho__nav a:hover { color: var(--cor-azul); }
@media (min-width: 900px) {
  .cabecalho__menu { display: none; }
  .cabecalho__nav { display: flex; flex-direction: row; width: auto; padding: 0; order: 0; gap: 1.25rem; }
}
</style>
