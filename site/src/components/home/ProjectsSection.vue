<script setup lang="ts">
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { perfil, projetos } from "../../content/perfil"
import CarrosselItens from "../comum/CarrosselItens.vue"
import ProjectCard from "./ProjectCard.vue"

const { t } = useI18n()
const c = useConteudo()
</script>

<template>
  <section id="projetos" class="secao" aria-labelledby="projetos-titulo">
    <div class="container">
      <div class="secao__cabecalho projetos__cabecalho">
        <h2 id="projetos-titulo">{{ c.projetos.titulo }}</h2>
        <p class="secao__subtitulo">{{ c.projetos.subtitulo }}</p>
      </div>
      <CarrosselItens :rotulo="c.projetos.titulo">
        <ProjectCard v-for="p in projetos" :key="p.id" :projeto="p" />
      </CarrosselItens>
      <p class="projetos__todos">
        <a class="botao botao--secundario" :href="perfil.repositorios" target="_blank" rel="noopener">{{ t("projetos.verTodos") }}</a>
      </p>
    </div>
  </section>
</template>

<style scoped>
.projetos__cabecalho { grid-template-columns: minmax(0, 1fr); }
@media (min-width: 900px) { .projetos__cabecalho { grid-template-columns: 1fr 1fr; align-items: end; gap: 2rem; } }
.projetos__todos { margin: 1.5rem 0 0; }
</style>
