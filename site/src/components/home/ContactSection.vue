<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { cv, perfil } from "../../content/perfil"
import type { Idioma } from "../../i18n"

const { t, locale } = useI18n()
const c = useConteudo()
const arquivoCv = computed(() => cv[locale.value as Idioma])
</script>

<template>
  <section id="contato" class="secao" aria-labelledby="contato-titulo">
    <div class="container">
      <h2 id="contato-titulo">{{ c.contato.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.contato.texto }}</p>
      <ul class="contato__links">
        <li>
          <a class="botao" :href="`mailto:${perfil.email}`" data-testid="contato-email">{{ t("contato.email") }}: {{ perfil.email }}</a>
        </li>
        <li><a class="botao botao--secundario" :href="perfil.linkedin" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a class="botao botao--secundario" :href="perfil.github" target="_blank" rel="noopener">GitHub</a></li>
        <li v-if="arquivoCv">
          <a class="botao botao--secundario" :href="arquivoCv" download data-testid="contato-cv">{{ t("contato.cv") }}</a>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.contato__links { list-style: none; padding: 0; margin: 1.5rem 0 0; display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>
