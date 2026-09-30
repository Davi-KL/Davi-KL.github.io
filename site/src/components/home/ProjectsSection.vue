<script setup lang="ts">
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { perfil, projetos } from "../../content/perfil"
import ProjectCard from "./ProjectCard.vue"

const { t } = useI18n()
const c = useConteudo()
</script>

<template>
  <section id="projetos" class="secao" aria-labelledby="projetos-titulo">
    <div class="container">
      <h2 id="projetos-titulo">{{ c.projetos.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.projetos.subtitulo }}</p>
      <div class="projetos__grade">
        <ProjectCard v-for="p in projetos" :key="p.id" :projeto="p" />
      </div>
      <p class="projetos__todos">
        <a :href="perfil.repositorios" target="_blank" rel="noopener">{{ t("projetos.verTodos") }} →</a>
      </p>
    </div>
  </section>
</template>

<style scoped>
.projetos__grade { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); }
.projetos__todos { margin-top: 1.5rem; }
</style>
