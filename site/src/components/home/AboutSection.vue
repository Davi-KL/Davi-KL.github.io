<script setup lang="ts">
import { useConteudo } from "../../composables/useConteudo"
import { type GrupoStack, stack } from "../../content/perfil"

const c = useConteudo()
const grupos = Object.keys(stack) as GrupoStack[]
</script>

<template>
  <section id="sobre" class="secao" aria-labelledby="sobre-titulo">
    <div class="container sobre">
      <div>
        <h2 id="sobre-titulo">{{ c.sobre.titulo }}</h2>
        <p v-for="(paragrafo, i) in c.sobre.paragrafos" :key="i">{{ paragrafo }}</p>
        <h3>{{ c.sobre.formacaoTitulo }}</h3>
        <ul class="lista">
          <li v-for="f in c.sobre.formacao" :key="f.instituicao">
            <strong>{{ f.curso }}</strong> — {{ f.instituicao }}<span v-if="f.periodo" class="suave"> · {{ f.periodo }}</span>
          </li>
        </ul>
        <h3>{{ c.sobre.certificacoesTitulo }}</h3>
        <ul class="lista">
          <li v-for="item in c.sobre.certificacoes" :key="item">{{ item }}</li>
        </ul>
        <h3>{{ c.sobre.idiomasTitulo }}</h3>
        <ul class="lista">
          <li v-for="item in c.sobre.idiomas" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="cartao">
        <h3>{{ c.sobre.stackTitulo }}</h3>
        <div v-for="g in grupos" :key="g" class="stack__grupo">
          <p class="stack__rotulo">{{ c.sobre.grupos[g] }}</p>
          <ul class="etiquetas">
            <li v-for="tec in stack[g]" :key="tec">{{ tec }}</li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sobre { display: grid; gap: 2rem; }
@media (min-width: 900px) { .sobre { grid-template-columns: 3fr 2fr; align-items: start; } }
.lista { padding-left: 1.1rem; margin: 0 0 1.25rem; }
.stack__grupo + .stack__grupo { margin-top: 1rem; }
.stack__rotulo { font-size: 0.8125rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--cor-texto-suave); margin-bottom: 0.5rem; }
</style>
