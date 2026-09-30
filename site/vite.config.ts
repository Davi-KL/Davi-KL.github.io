/// <reference types="vitest/config" />
import vue from "@vitejs/plugin-vue"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [vue()],
  base: "/",
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
  build: { chunkSizeWarningLimit: 1500 },
  test: {
    environment: "jsdom",
    include: ["tests/**/*.spec.ts"],
    setupFiles: ["tests/setup.ts"],
    restoreMocks: true,
    unstubGlobals: true,
  },
})
