<script setup lang="ts">
import { computed } from "vue"
import { useConteudo } from "../../composables/useConteudo"
import CarrosselItens from "../comum/CarrosselItens.vue"

const c = useConteudo()
const destaque = computed(() => c.value.experiencia.destaque)
const cores = ["ambar", "ciano", "verde", "coral"]

// Cada item tem o formato "Termo-chave: descrição". O termo vira o chip; o resto, o texto de apoio.
function separar(texto: string): { rotulo: string; corpo: string } {
  const i = texto.indexOf(":")
  return i > 0 ? { rotulo: texto.slice(0, i), corpo: texto.slice(i + 1).trim() } : { rotulo: texto, corpo: "" }
}
</script>

<template>
  <section id="experiencia" class="secao" aria-labelledby="experiencia-titulo">
    <div class="container">
      <div class="secao__cabecalho">
        <h2 id="experiencia-titulo">{{ c.experiencia.titulo }}</h2>
      </div>

      <article class="destaque" data-testid="sarah">
        <header class="destaque__cabecalho">
          <span class="chip chip--ambar">{{ destaque.periodo }}</span>
          <span class="suave">{{ destaque.local }}</span>
          <h3 class="destaque__cargo">{{ destaque.cargo }}</h3>
          <p class="destaque__empresa">{{ destaque.empresa }}</p>
        </header>
        <ul class="destaque__pontos">
          <li v-for="(item, i) in destaque.itens" :key="i">
            <span :class="['chip', `chip--${cores[i % cores.length]}`]">{{ separar(item).rotulo }}</span>
            <p v-if="separar(item).corpo">{{ separar(item).corpo }}</p>
          </li>
        </ul>
      </article>

      <div class="outras">
        <h3 class="outras__titulo">{{ c.experiencia.outrasTitulo }}</h3>
        <CarrosselItens :rotulo="c.experiencia.outrasTitulo">
          <article v-for="o in c.experiencia.outras" :key="o.empresa" class="cartao carrossel__item outra">
            <span class="chip chip--ciano">{{ o.periodo }}</span>
            <h4 class="outra__cargo">{{ o.cargo }}</h4>
            <p class="suave">{{ o.empresa }}</p>
          </article>
        </CarrosselItens>
      </div>
    </div>
  </section>
</template>

<style scoped>
.destaque {
  position: relative;
  background: var(--cor-superficie);
  border: 1px solid var(--cor-borda);
  border-radius: var(--raio-grande);
  padding: clamp(1.5rem, 4vw, 2.5rem);
  overflow: hidden;
}
.destaque::before {
  content: ""; position: absolute; inset: 0 auto 0 0; width: 5px;
  background: var(--cor-destaque);
}
.destaque__cabecalho { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; margin-bottom: 2rem; }
.destaque__cabecalho .suave { font-size: 0.9375rem; }
.destaque__cargo { width: 100%; margin: 0.5rem 0 0; font-size: clamp(1.6rem, 3.4vw, 2.2rem); }
.destaque__empresa { width: 100%; margin: 0; color: var(--cor-texto-suave); }

.destaque__pontos { min-width: 0; list-style: none; padding: 0; margin: 0; display: grid; gap: 1.5rem 2rem; }
@media (min-width: 760px) { .destaque__pontos { grid-template-columns: 1fr 1fr; } }
.destaque__pontos li { display: grid; gap: 0.6rem; align-content: start; }
.destaque__pontos p { margin: 0; color: var(--cor-texto); font-size: 0.975rem; }

.outras { margin-top: clamp(3rem, 7vw, 4.5rem); }
.outras__titulo { font-size: 1.5rem; margin-bottom: 1.25rem; }
.outra { gap: 0.75rem; min-height: 100%; }
.outra__cargo { font-size: 1.15rem; margin: 0; }
.outra p { margin: 0; }
</style>
