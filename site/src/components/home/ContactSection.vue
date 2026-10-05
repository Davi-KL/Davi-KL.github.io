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
    <div class="container contato">
      <h2 id="contato-titulo">{{ c.contato.titulo }}</h2>
      <p class="contato__texto">{{ c.contato.texto }}</p>
      <a class="contato__email" :href="`mailto:${perfil.email}`" data-testid="contato-email">
        <span class="contato__rotulo">{{ t("contato.email") }}</span>
        {{ perfil.email }}
      </a>
      <ul class="contato__links">
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
.contato {
  display: grid; gap: 1.25rem; justify-items: start;
  padding: clamp(2rem, 6vw, 4rem);
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda); border-radius: var(--raio-grande);
}
.contato__texto { margin: 0; color: var(--cor-texto-suave); max-width: 56ch; }
.contato__email {
  font-family: var(--fonte-display); font-weight: 750; font-variation-settings: "wdth" 88;
  font-size: clamp(1.5rem, 4.5vw, 2.8rem); letter-spacing: -0.02em; line-height: 1.1;
  color: var(--cor-destaque); text-decoration: none; overflow-wrap: anywhere;
  border-bottom: 3px solid color-mix(in srgb, var(--cor-destaque) 35%, transparent);
  transition: border-color 0.2s ease, color 0.2s ease;
}
.contato__email:hover { color: var(--cor-texto-forte); border-color: var(--cor-texto-forte); }
.contato__rotulo { display: block; font-family: var(--fonte); font-size: 0.95rem; font-weight: 550; color: var(--cor-texto-suave); letter-spacing: 0; margin-bottom: 0.25rem; }
.contato__links { list-style: none; padding: 0; margin: 0.75rem 0 0; display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>
