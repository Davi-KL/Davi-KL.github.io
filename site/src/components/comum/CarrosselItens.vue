<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue"
import { useI18n } from "vue-i18n"

defineProps<{ rotulo: string }>()

const { t } = useI18n()
const trilho = ref<HTMLElement | null>(null)
const podeVoltar = ref(false)
const podeAvancar = ref(true)
const progresso = ref(0)

function atualizar(): void {
  const el = trilho.value
  if (!el) return
  const maximo = el.scrollWidth - el.clientWidth
  podeVoltar.value = el.scrollLeft > 4
  podeAvancar.value = el.scrollLeft < maximo - 4
  progresso.value = maximo > 0 ? el.scrollLeft / maximo : 0
}

function mover(direcao: 1 | -1): void {
  const el = trilho.value
  if (!el) return
  el.scrollBy({ left: direcao * el.clientWidth * 0.8, behavior: "smooth" })
}

onMounted(() => {
  atualizar()
  window.addEventListener("resize", atualizar)
})
onBeforeUnmount(() => window.removeEventListener("resize", atualizar))
</script>

<template>
  <div class="carrossel" role="region" aria-roledescription="carrossel" :aria-label="rotulo">
    <div class="carrossel__controles">
      <div class="carrossel__barra" aria-hidden="true">
        <span class="carrossel__preenchido" :style="{ transform: `scaleX(${Math.max(progresso, 0.08)})` }"></span>
      </div>
      <div class="carrossel__botoes">
        <button type="button" class="carrossel__seta" :disabled="!podeVoltar" :aria-label="t('carrossel.anterior')" @click="mover(-1)">
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
        </button>
        <button type="button" class="carrossel__seta" :disabled="!podeAvancar" :aria-label="t('carrossel.proximo')" @click="mover(1)">
          <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
        </button>
      </div>
    </div>
    <div ref="trilho" class="carrossel__trilho" tabindex="0" @scroll.passive="atualizar">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.carrossel { display: grid; gap: 1.25rem; min-width: 0; }
.carrossel__controles { display: flex; align-items: center; gap: 1.25rem; }
.carrossel__barra {
  flex: 1; height: 3px; border-radius: 3px; background: var(--cor-borda); overflow: hidden;
}
.carrossel__preenchido {
  display: block; width: 100%; height: 100%; background: var(--cor-destaque);
  transform-origin: left; transition: transform 0.25s ease;
}
.carrossel__botoes { display: flex; gap: 0.5rem; }
.carrossel__seta {
  width: 44px; height: 44px; display: grid; place-items: center;
  border-radius: 12px; border: 1px solid var(--cor-borda);
  background: var(--cor-superficie); color: var(--cor-texto-forte); cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}
.carrossel__seta:hover:not(:disabled) { border-color: var(--cor-destaque); background: var(--cor-superficie-2); }
.carrossel__seta:disabled { opacity: 0.35; cursor: default; }
.carrossel__trilho {
  display: flex; gap: 1rem; overflow-x: auto;
  scroll-snap-type: x mandatory; scroll-padding-inline: 0;
  overscroll-behavior-x: contain; scrollbar-width: none;
  padding: 0.25rem 0.25rem 1rem; margin: 0 -0.25rem;
}
.carrossel__trilho::-webkit-scrollbar { display: none; }
.carrossel__trilho:focus-visible { border-radius: var(--raio); }

:slotted(.carrossel__item) {
  flex: 0 0 min(86%, 380px);
  scroll-snap-align: start;
  display: flex; flex-direction: column;
}
@media (min-width: 900px) {
  :slotted(.carrossel__item--larga) { flex-basis: min(60%, 620px); }
}
</style>
