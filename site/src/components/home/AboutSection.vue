<script setup lang="ts">
import { useConteudo } from "../../composables/useConteudo"
import { type GrupoStack, stack } from "../../content/perfil"

const c = useConteudo()
const grupos = Object.keys(stack) as GrupoStack[]
const cores: Record<GrupoStack, string> = { front: "ciano", back: "ambar", dados: "verde", devops: "coral" }
</script>

<template>
  <section id="sobre" class="secao" aria-labelledby="sobre-titulo">
    <div class="container">
      <div class="sobre__topo">
        <div class="sobre__texto">
          <h2 id="sobre-titulo">{{ c.sobre.titulo }}</h2>
          <p v-for="(paragrafo, i) in c.sobre.paragrafos" :key="i" class="sobre__paragrafo">{{ paragrafo }}</p>
        </div>
        <div class="sobre__fichas">
          <div class="ficha">
            <h3>{{ c.sobre.formacaoTitulo }}</h3>
            <ul class="formacao">
              <li v-for="f in c.sobre.formacao" :key="f.instituicao">
                <strong>{{ f.curso }}</strong>
                <span>{{ f.instituicao }}</span>
                <span v-if="f.periodo" class="suave">{{ f.periodo }}</span>
              </li>
            </ul>
          </div>
          <div class="ficha">
            <h3>{{ c.sobre.certificacoesTitulo }}</h3>
            <ul class="etiquetas">
              <li v-for="item in c.sobre.certificacoes" :key="item"><span class="chip chip--verde">{{ item }}</span></li>
            </ul>
          </div>
          <div class="ficha">
            <h3>{{ c.sobre.idiomasTitulo }}</h3>
            <ul class="etiquetas">
              <li v-for="item in c.sobre.idiomas" :key="item"><span class="chip chip--ciano">{{ item }}</span></li>
            </ul>
          </div>
        </div>
      </div>

      <div class="stack">
        <h3 class="stack__titulo">{{ c.sobre.stackTitulo }}</h3>
        <div class="stack__grade">
          <article v-for="g in grupos" :key="g" class="cartao stack__grupo">
            <p class="stack__rotulo">{{ c.sobre.grupos[g] }}</p>
            <ul class="stack__chips">
              <li v-for="tec in stack[g]" :key="tec"><span :class="['chip', `chip--${cores[g]}`]">{{ tec }}</span></li>
            </ul>
          </article>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.sobre__topo { display: grid; grid-template-columns: minmax(0, 1fr); gap: 2.5rem; }
@media (min-width: 900px) { .sobre__topo { grid-template-columns: 1.1fr 0.9fr; align-items: start; gap: 3.5rem; } }
.sobre__texto h2 { margin-bottom: 1.25rem; }
.sobre__paragrafo { font-size: 1.1rem; color: var(--cor-texto); max-width: 62ch; }

.sobre__fichas { display: grid; gap: 1.5rem; }
.ficha h3 { font-size: 1.05rem; color: var(--cor-texto-suave); font-family: var(--fonte); font-weight: 600; letter-spacing: 0; margin-bottom: 0.75rem; }
.formacao { list-style: none; padding: 0; margin: 0; display: grid; gap: 0.9rem; }
.formacao li {
  display: grid; gap: 0.1rem; padding-left: 1rem;
  border-left: 2px solid var(--cor-borda);
}
.formacao strong { color: var(--cor-texto-forte); font-weight: 650; }
.formacao span { font-size: 0.9375rem; }
.ficha .etiquetas li { background: none; padding: 0; }

.stack { margin-top: clamp(3.5rem, 8vw, 5rem); }
.stack__titulo { font-size: 1.5rem; margin-bottom: 1.25rem; }
.stack__grade { display: grid; grid-template-columns: minmax(0, 1fr); gap: 1rem; }
@media (min-width: 700px) { .stack__grade { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.stack__grupo { display: flex; flex-direction: column; gap: 1rem; }
.stack__rotulo { margin: 0; font-family: var(--fonte-display); font-weight: 700; font-size: 1.2rem; color: var(--cor-texto-forte); }
.stack__chips { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 0.5rem; }
</style>
