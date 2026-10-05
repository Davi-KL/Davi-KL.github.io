<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { type GrupoStack, type Projeto, stack } from "../../content/perfil"

const props = defineProps<{ projeto: Projeto }>()
const { t } = useI18n()
const c = useConteudo()
const item = computed(() => c.value.projetos.itens[props.projeto.id])

const cores: Record<GrupoStack, string> = { front: "ciano", back: "ambar", dados: "verde", devops: "coral" }
const grupos = Object.keys(stack) as GrupoStack[]

// Tecnologias conhecidas da stack ganham a cor do grupo; as demais ficam neutras.
function grupoDe(tag: string): GrupoStack | null {
  return grupos.find((g) => stack[g].includes(tag)) ?? null
}
const corPrincipal = computed(() => {
  const primeiro = props.projeto.tags.map(grupoDe).find((g): g is GrupoStack => g !== null)
  return primeiro ? cores[primeiro] : "ciano"
})
</script>

<template>
  <article class="projeto cartao carrossel__item" :data-testid="`projeto-${projeto.id}`" :style="{ '--faixa': `var(--cor-${corPrincipal})` }">
    <h3 class="projeto__titulo">{{ item.titulo }}</h3>
    <p class="projeto__descricao">{{ item.descricao }}</p>
    <p class="projeto__papel">
      <span class="chip chip--ambar">{{ t("projetos.papel") }}</span>
      <span>{{ item.papel }}</span>
    </p>
    <ul class="projeto__tags">
      <li v-for="tag in projeto.tags" :key="tag">
        <span v-if="grupoDe(tag)" :class="['chip', `chip--${cores[grupoDe(tag) as GrupoStack]}`]">{{ tag }}</span>
        <span v-else class="etiqueta">{{ tag }}</span>
      </li>
    </ul>
    <div class="projeto__links">
      <template v-for="link in projeto.links" :key="link.url">
        <RouterLink v-if="link.interno" class="botao" :to="link.url">{{ t(`projetos.links.${link.tipo}`) }}</RouterLink>
        <a v-else class="botao botao--secundario" :href="link.url" target="_blank" rel="noopener">
          {{ t(`projetos.links.${link.tipo}`) }}
        </a>
      </template>
    </div>
  </article>
</template>

<style scoped>
.projeto {
  position: relative; gap: 1rem; padding: 1.75rem;
  border-radius: var(--raio-grande);
  background: linear-gradient(180deg, color-mix(in srgb, var(--faixa) 6%, var(--cor-superficie)) 0%, var(--cor-superficie) 38%);
}
.projeto__titulo { font-size: 1.75rem; margin: 0; }
.projeto__descricao { margin: 0; color: var(--cor-texto); font-size: 0.975rem; }
.projeto__papel {
  margin: 0; display: grid; gap: 0.5rem; justify-items: start;
  font-size: 0.9375rem; color: var(--cor-texto-forte);
  padding: 0.85rem 1rem; border-radius: 12px;
  background: color-mix(in srgb, var(--cor-destaque) 7%, transparent);
  border: 1px dashed color-mix(in srgb, var(--cor-destaque) 35%, transparent);
}
.projeto__tags { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 0.45rem; }
.etiqueta {
  display: inline-flex; padding: 0.3rem 0.7rem; border-radius: 999px;
  font-size: 0.8125rem; font-weight: 550; color: var(--cor-texto);
  background: var(--cor-superficie-2); border: 1px solid var(--cor-borda);
}
.projeto__links { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: auto; padding-top: 0.5rem; }
</style>
