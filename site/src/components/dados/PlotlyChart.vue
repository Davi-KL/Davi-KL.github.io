<script setup lang="ts">
import type PlotlyTipo from "plotly.js-basic-dist-min"
import { onBeforeUnmount, onMounted, ref, watch } from "vue"
import { CONFIG_BASE, mesclarLayout } from "../../lib/chartTheme"
import type { Traco } from "../../lib/graficos"

const props = withDefaults(
  defineProps<{ dados: Traco[]; rotulo: string; layout?: Record<string, unknown>; altura?: number }>(),
  { layout: () => ({}), altura: 380 },
)

const alvo = ref<HTMLDivElement | null>(null)
let plotly: typeof PlotlyTipo | null = null
let visivel = false
let observador: IntersectionObserver | null = null

async function desenhar(): Promise<void> {
  if (!alvo.value || !visivel) return
  plotly ??= (await import("plotly.js-basic-dist-min")).default
  await plotly.react(alvo.value, props.dados, mesclarLayout(props.layout, props.altura), CONFIG_BASE)
}

onMounted(() => {
  if (!("IntersectionObserver" in window)) {
    visivel = true
    void desenhar()
    return
  }
  observador = new IntersectionObserver(
    (entradas) => {
      if (entradas.some((e) => e.isIntersecting)) {
        visivel = true
        observador?.disconnect()
        void desenhar()
      }
    },
    { rootMargin: "200px" },
  )
  if (alvo.value) observador.observe(alvo.value)
})

watch(() => [props.dados, props.layout, props.altura], () => void desenhar(), { deep: true })

onBeforeUnmount(() => {
  observador?.disconnect()
  if (alvo.value && plotly) plotly.purge(alvo.value)
})
</script>

<template>
  <div ref="alvo" class="grafico" role="img" :aria-label="rotulo" :style="{ minHeight: `${altura}px` }"></div>
</template>

<style scoped>
.grafico { width: 100%; }
</style>
