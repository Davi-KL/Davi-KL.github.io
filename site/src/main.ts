import "@fontsource-variable/bricolage-grotesque"
import "@fontsource-variable/instrument-sans"
import "./styles/tokens.css"
import "./styles/base.css"
import { createApp } from "vue"
import App from "./App.vue"
import { aplicarLang, i18n, type Idioma } from "./i18n"
import { criarRouter } from "./router"

aplicarLang(i18n.global.locale.value as Idioma)
createApp(App).use(i18n).use(criarRouter()).mount("#app")
