import { createRouter, createWebHistory, type RouterHistory } from "vue-router"

export function criarRouter(history: RouterHistory = createWebHistory(import.meta.env.BASE_URL)) {
  return createRouter({ history, routes: [{ path: "/", component: { template: "<div />" } }] })
}
