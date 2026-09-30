import { createRouter, createWebHistory, type RouterHistory } from "vue-router"
import HomeView from "./views/HomeView.vue"

export function criarRouter(history: RouterHistory = createWebHistory(import.meta.env.BASE_URL)) {
  return createRouter({
    history,
    routes: [
      { path: "/", name: "home", component: HomeView },
      { path: "/dados-combustiveis", name: "dados", component: () => import("./views/FuelDataView.vue") },
      { path: "/:caminho(.*)*", redirect: "/" },
    ],
    scrollBehavior(to, _from, salvo) {
      if (salvo) return salvo
      if (to.hash) return { el: to.hash }
      return { top: 0 }
    },
  })
}
