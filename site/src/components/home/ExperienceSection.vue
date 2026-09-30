<script setup lang="ts">
import { computed } from "vue"
import { useConteudo } from "../../composables/useConteudo"

const c = useConteudo()
const destaque = computed(() => c.value.experiencia.destaque)
</script>

<template>
  <section id="experiencia" class="secao" aria-labelledby="experiencia-titulo">
    <div class="container">
      <h2 id="experiencia-titulo">{{ c.experiencia.titulo }}</h2>
      <article class="cartao experiencia" data-testid="sarah">
        <p class="experiencia__periodo">{{ destaque.periodo }} · {{ destaque.local }}</p>
        <h3>{{ destaque.cargo }}</h3>
        <p class="experiencia__empresa">{{ destaque.empresa }}</p>
        <ul>
          <li v-for="(item, i) in destaque.itens" :key="i">{{ item }}</li>
        </ul>
      </article>
      <h3 class="outras__titulo">{{ c.experiencia.outrasTitulo }}</h3>
      <ul class="outras">
        <li v-for="o in c.experiencia.outras" :key="o.empresa">
          <strong>{{ o.cargo }}</strong> — {{ o.empresa }} <span class="suave">· {{ o.periodo }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.experiencia { border-left: 4px solid var(--cor-azul); }
.experiencia__periodo { font-size: 0.875rem; color: var(--cor-texto-suave); margin-bottom: 0.25rem; }
.experiencia__empresa { color: var(--cor-azul); font-weight: 500; }
.experiencia ul { padding-left: 1.1rem; margin: 0; display: grid; gap: 0.5rem; }
.outras__titulo { margin-top: 2rem; }
.outras { padding-left: 1.1rem; }
</style>
