<script setup lang="ts">
import { watchEffect } from "vue"
import { useI18n } from "vue-i18n"
import type { Idioma } from "../i18n"
import { aplicarMeta } from "../lib/seo"

const { t, locale } = useI18n()
watchEffect(() =>
  aplicarMeta({ titulo: t("meta.tituloHome"), descricao: t("meta.descricaoHome"), idioma: locale.value as Idioma }),
)
</script>

<template>
  <main id="conteudo"></main>
</template>
