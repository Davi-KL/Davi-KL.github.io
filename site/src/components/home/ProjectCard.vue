<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import type { Projeto } from "../../content/perfil"

const props = defineProps<{ projeto: Projeto }>()
const { t } = useI18n()
const c = useConteudo()
const item = computed(() => c.value.projetos.itens[props.projeto.id])
</script>

<template>
  <article class="cartao projeto" :data-testid="`projeto-${projeto.id}`">
    <h3>{{ item.titulo }}</h3>
    <p class="projeto__descricao">{{ item.descricao }}</p>
    <p class="projeto__papel"><strong>{{ t("projetos.papel") }}:</strong> {{ item.papel }}</p>
    <ul class="etiquetas">
      <li v-for="tag in projeto.tags" :key="tag">{{ tag }}</li>
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
.projeto { display: flex; flex-direction: column; gap: 0.75rem; }
.projeto h3 { margin: 0; }
.projeto__descricao { margin: 0; color: var(--cor-texto); }
.projeto__papel { margin: 0; font-size: 0.9375rem; color: var(--cor-texto-suave); }
.projeto__papel strong { color: var(--cor-verde); }
.projeto__links { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: auto; padding-top: 0.5rem; }
</style>
