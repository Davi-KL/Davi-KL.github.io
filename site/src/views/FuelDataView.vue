<script setup lang="ts">
import { computed, watchEffect } from "vue"
import { useI18n } from "vue-i18n"
import EstadoDados from "../components/dados/EstadoDados.vue"
import EthanolPanel from "../components/dados/EthanolPanel.vue"
import EvolutionPanel from "../components/dados/EvolutionPanel.vue"
import MethodologySection from "../components/dados/MethodologySection.vue"
import RankingPanel from "../components/dados/RankingPanel.vue"
import { useConteudo } from "../composables/useConteudo"
import { useFuelData } from "../composables/useFuelData"
import type { Idioma } from "../i18n"
import { formatarData, formatarDiaMes } from "../lib/format"
import { aplicarMeta } from "../lib/seo"
import { dadosDesatualizados } from "../lib/stale"
import type { EtanolGasolina, Evolucao, Meta, Ranking } from "../types/dados"

const { t, locale } = useI18n()
const c = useConteudo()
const idioma = computed(() => locale.value as Idioma)

const { dados: meta } = useFuelData<Meta>("meta.json")
const { dados: evolucao, erro: erroEvolucao, carregando: carregandoEvolucao } = useFuelData<Evolucao>("evolucao.json")
const { dados: ranking, erro: erroRanking, carregando: carregandoRanking } = useFuelData<Ranking>("ranking_uf.json")
const { dados: etanol, erro: erroEtanol, carregando: carregandoEtanol } = useFuelData<EtanolGasolina>("etanol_gasolina.json")

// Cada seção mostra seu próprio estado (carregando/erro/pronta) de forma independente: uma
// análise lenta ou com erro não pode travar as outras que já chegaram (Foco de revisão nº 1).
// A altura mínima reservada em EstadoDados evita que o conteúdo "pule" ao chegar (CLS).
const desatualizado = computed(() => meta.value !== null && dadosDesatualizados(meta.value.semana_mais_recente, new Date()))

watchEffect(() =>
  aplicarMeta({ titulo: t("meta.tituloDados"), descricao: t("meta.descricaoDados"), idioma: idioma.value }),
)
</script>

<template>
  <main id="conteudo" class="container pagina-dados">
    <RouterLink to="/" class="voltar">← {{ t("dados.voltar") }}</RouterLink>
    <header class="pagina-dados__cabecalho">
      <h1>{{ c.dados.titulo }}</h1>
      <p class="secao__subtitulo">{{ c.dados.intro }}</p>
      <p class="pagina-dados__atualizacao">
        <template v-if="meta">
          {{ t("dados.dadosAte", { data: formatarData(meta.semana_mais_recente, idioma) }) }}
          <span v-if="desatualizado" class="selo-aviso" data-testid="aviso-desatualizado">
            {{ t("dados.desatualizado", { data: formatarDiaMes(meta.semana_mais_recente, idioma) }) }}
          </span>
        </template>
      </p>
    </header>

    <section class="analise" aria-labelledby="evolucao-titulo" data-testid="analise-evolucao">
      <h2 id="evolucao-titulo">{{ c.dados.evolucao.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.dados.evolucao.explicacao }}</p>
      <EstadoDados :carregando="carregandoEvolucao" :erro="erroEvolucao">
        <EvolutionPanel v-if="evolucao" :evolucao="evolucao" />
      </EstadoDados>
    </section>

    <section class="analise" aria-labelledby="ranking-titulo" data-testid="analise-ranking">
      <h2 id="ranking-titulo">{{ c.dados.ranking.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.dados.ranking.explicacao }}</p>
      <EstadoDados :carregando="carregandoRanking" :erro="erroRanking">
        <RankingPanel v-if="ranking" :ranking="ranking" />
      </EstadoDados>
    </section>

    <section class="analise" aria-labelledby="etanol-titulo" data-testid="analise-etanol">
      <h2 id="etanol-titulo">{{ c.dados.etanol.titulo }}</h2>
      <p class="secao__subtitulo">{{ c.dados.etanol.explicacao }}</p>
      <EstadoDados :carregando="carregandoEtanol" :erro="erroEtanol">
        <EthanolPanel v-if="etanol" :etanol-gasolina="etanol" />
      </EstadoDados>
    </section>

    <MethodologySection :meta="meta" />
  </main>
</template>

<style scoped>
.pagina-dados { padding-block: 2rem 4rem; }
.voltar { display: inline-flex; align-items: center; min-height: 44px; }
.pagina-dados__cabecalho { padding-block: 1.5rem 1rem; }
.pagina-dados__atualizacao { color: var(--cor-texto-suave); font-size: 0.9375rem; min-height: 1.6em; }
.selo-aviso {
  display: inline-block; margin-left: 0.5rem; padding: 0.125rem 0.625rem;
  border-radius: 999px; border: 1px solid var(--cor-destaque); color: var(--cor-destaque); font-size: 0.8125rem;
}
.analise { padding-block: 2.5rem; border-top: 1px solid var(--cor-borda); }
:deep(.insight) {
  margin-top: 1rem; padding: 0.875rem 1rem; border-left: 4px solid var(--cor-verde);
  background: var(--cor-superficie); border-radius: 0 8px 8px 0; color: var(--cor-texto-forte);
}
</style>
