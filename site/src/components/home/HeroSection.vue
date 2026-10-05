<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { cv, perfil, projetos } from "../../content/perfil"
import type { Idioma } from "../../i18n"

const { t, locale } = useI18n()
const c = useConteudo()
const arquivoCv = computed(() => cv[locale.value as Idioma])
const fotoSrc = `${import.meta.env.BASE_URL}foto-davi.jpg`
</script>

<template>
  <section class="hero" aria-labelledby="hero-titulo">
    <div class="container hero__layout">
      <div class="hero__texto">
        <p class="hero__cargo">{{ perfil.nome }} · {{ c.hero.titulo }}</p>
        <h1 id="hero-titulo"><span class="hero__linha">{{ c.hero.frase1 }}</span> <span class="hero__linha">{{ c.hero.frase2 }}</span></h1>
        <p class="hero__resumo">{{ c.hero.resumo }}</p>
        <div class="hero__acoes">
          <a class="botao" href="#projetos">{{ t("hero.verProjetos") }}</a>
          <a v-if="arquivoCv" class="botao botao--secundario" :href="arquivoCv" download>{{ t("hero.baixarCv") }}</a>
          <a class="botao botao--secundario" :href="perfil.github" target="_blank" rel="noopener">GitHub</a>
          <a class="botao botao--secundario" :href="perfil.linkedin" target="_blank" rel="noopener">LinkedIn</a>
        </div>
      </div>

      <figure class="hero__visual">
        <img class="hero__foto" :src="fotoSrc" :alt="t('hero.fotoAlt')" data-testid="hero-foto" width="480" height="600" />
        <div class="placa" data-testid="hero-placa">
          <div class="placa__item">
            <span class="placa__valor">2+</span>
            <span class="placa__rotulo">{{ t("hero.statAnos") }}</span>
          </div>
          <div class="placa__item">
            <span class="placa__valor placa__valor--verde">{{ projetos.length }}</span>
            <span class="placa__rotulo">{{ t("hero.statProjetos") }}</span>
          </div>
        </div>
      </figure>
    </div>
  </section>
</template>

<style scoped>
.hero { padding-block: clamp(3rem, 9vw, 6.5rem) clamp(3rem, 8vw, 5rem); }
.hero__layout { display: grid; grid-template-columns: minmax(0, 1fr); gap: clamp(2.5rem, 6vw, 4rem); align-items: center; }
@media (min-width: 900px) { .hero__layout { grid-template-columns: 1.15fr 0.85fr; } }

.hero__cargo { color: var(--cor-texto-suave); font-weight: 550; margin-bottom: 1.25rem; }
.hero__linha { display: block; }
.hero__resumo { font-size: 1.2rem; max-width: 52ch; color: var(--cor-texto); margin: 1.5rem 0 2rem; }
.hero__acoes { display: flex; flex-wrap: wrap; gap: 0.75rem; }

.hero__visual { position: relative; min-width: 0; margin: 0; justify-self: center; width: min(100%, 420px); }
.hero__foto {
  width: 100%; aspect-ratio: 4 / 5; object-fit: cover; object-position: center 20%;
  border-radius: var(--raio-grande);
  border: 1px solid var(--cor-borda);
  animation: entrada 0.9s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}

/* Placa de preço de posto: o único elemento com brilho da página. */
.placa {
  position: absolute; left: 0; right: 0; bottom: -8%;
  margin-inline: auto; width: 92%;
  display: grid; grid-template-columns: 1fr 1fr;
  background: #0a0c10;
  border: 1px solid color-mix(in srgb, var(--cor-destaque) 35%, var(--cor-borda));
  border-radius: 18px;
  box-shadow: 0 24px 60px -20px rgba(0, 0, 0, 0.7), 0 0 0 6px var(--cor-fundo);
  animation: entrada 0.9s 0.2s cubic-bezier(0.2, 0.7, 0.2, 1) both;
}
.placa__item { display: grid; padding: 1rem 1.1rem 1.1rem; }
.placa__item + .placa__item { border-left: 1px dashed color-mix(in srgb, var(--cor-destaque) 25%, transparent); }
.placa__valor {
  font-family: var(--fonte-display); font-weight: 800; font-size: clamp(2.6rem, 6vw, 3.4rem);
  line-height: 1; color: var(--cor-destaque); font-variant-numeric: tabular-nums;
  text-shadow: 0 0 22px color-mix(in srgb, var(--cor-destaque) 45%, transparent);
}
.placa__valor--verde { color: var(--cor-verde); text-shadow: 0 0 22px color-mix(in srgb, var(--cor-verde) 40%, transparent); }
.placa__rotulo { font-size: 0.875rem; color: var(--cor-texto-suave); margin-top: 0.5rem; line-height: 1.35; }

@keyframes entrada {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: none; }
}
</style>
