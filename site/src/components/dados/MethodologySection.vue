<script setup lang="ts">
import { computed } from "vue"
import { useI18n } from "vue-i18n"
import { useConteudo } from "../../composables/useConteudo"
import { perfil } from "../../content/perfil"
import type { Idioma } from "../../i18n"
import { formatarMes, formatarNumero } from "../../lib/format"
import type { Meta } from "../../types/dados"

const props = defineProps<{ meta: Meta | null }>()
const { t, locale } = useI18n()
const c = useConteudo()
const idioma = computed(() => locale.value as Idioma)
const total = computed(() => (props.meta ? formatarNumero(props.meta.n_coletas_total, idioma.value) : null))
</script>

<template>
  <section class="analise" aria-labelledby="metodologia-titulo">
    <h2 id="metodologia-titulo">{{ c.dados.metodologia.titulo }}</h2>
    <ul class="metodologia">
      <li v-for="(item, i) in c.dados.metodologia.itens" :key="i">{{ item }}</li>
    </ul>
    <template v-if="meta">
      <p v-if="total" class="suave">{{ t("dados.totalColetas", { n: total }) }}</p>
      <p v-if="meta.ipca_em_cache" class="suave">{{ t("dados.ipcaCache", { mes: formatarMes(meta.ipca_ate, idioma) }) }}</p>
      <h3>{{ t("dados.fontes") }}</h3>
      <ul>
        <li v-for="f in meta.fontes" :key="f.url">
          <a :href="f.url" target="_blank" rel="noopener">{{ f.nome }}</a>
        </li>
      </ul>
    </template>
    <p>
      <a class="botao botao--secundario" :href="perfil.codigoPipeline" target="_blank" rel="noopener">{{ t("dados.verCodigo") }}</a>
    </p>
  </section>
</template>

<style scoped>
.metodologia { padding-left: 1.1rem; display: grid; gap: 0.5rem; max-width: 75ch; }
</style>
