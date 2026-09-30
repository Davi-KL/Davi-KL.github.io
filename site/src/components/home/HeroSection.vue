<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { useFuelData } from "../../composables/useFuelData"
import { cv, perfil, projetos } from "../../content/perfil"
import type { Idioma } from "../../i18n"
import { formatarReais } from "../../lib/format"
import type { Meta } from "../../types/dados"

const { t, locale } = useI18n()
const c = useConteudo()
const { dados: meta } = useFuelData<Meta>("meta.json")
const idioma = computed(() => locale.value as Idioma)
const arquivoCv = computed(() => cv[idioma.value])
const gasolinaDf = computed(() => (meta.value ? formatarReais(meta.value.destaques.gasolina_df, idioma.value) : null))
</script>

<template>
  <section class="hero" aria-labelledby="hero-titulo">
    <div class="container">
      <p class="hero__cargo">{{ perfil.nome }} · {{ c.hero.titulo }}</p>
      <h1 id="hero-titulo">{{ c.hero.frase1 }} <span class="hero__destaque">{{ c.hero.frase2 }}</span></h1>
      <p class="hero__resumo">{{ c.hero.resumo }}</p>
      <ul class="hero__numeros">
        <li class="numero">
          <span class="numero__valor">2+</span>
          <span class="numero__rotulo">{{ t("hero.statAnos") }}</span>
        </li>
        <li class="numero">
          <span class="numero__valor numero__valor--violeta">{{ projetos.length }}</span>
          <span class="numero__rotulo">{{ t("hero.statProjetos") }}</span>
        </li>
        <li v-if="gasolinaDf" class="numero" data-testid="gasolina-df">
          <span class="numero__valor numero__valor--verde">{{ gasolinaDf }}</span>
          <span class="numero__rotulo">{{ t("hero.statGasolina") }}</span>
        </li>
      </ul>
      <div class="hero__acoes">
        <a class="botao" href="#projetos">{{ t("hero.verProjetos") }}</a>
        <a v-if="arquivoCv" class="botao botao--secundario" :href="arquivoCv" download>{{ t("hero.baixarCv") }}</a>
        <a class="botao botao--secundario" :href="perfil.github" target="_blank" rel="noopener">GitHub</a>
        <a class="botao botao--secundario" :href="perfil.linkedin" target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero { padding-block: clamp(3rem, 10vw, 6rem) clamp(2.5rem, 8vw, 4rem); }
.hero__cargo { color: var(--cor-texto-suave); font-weight: 500; }
.hero__destaque { color: var(--cor-azul); display: block; }
.hero__resumo { font-size: 1.125rem; max-width: 60ch; color: var(--cor-texto); }
.hero__numeros {
  list-style: none; padding: 0; margin: 2rem 0;
  display: grid; gap: 0.75rem; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); max-width: 720px;
}
.numero { background: var(--cor-superficie); border: 1px solid var(--cor-borda); border-radius: var(--raio); padding: 1rem; }
.numero__valor { display: block; font-size: 1.75rem; font-weight: 700; color: var(--cor-azul); font-variant-numeric: tabular-nums; }
.numero__valor--violeta { color: var(--cor-violeta); }
.numero__valor--verde { color: var(--cor-verde); }
.numero__rotulo { font-size: 0.875rem; color: var(--cor-texto-suave); }
.hero__acoes { display: flex; flex-wrap: wrap; gap: 0.75rem; }
</style>
