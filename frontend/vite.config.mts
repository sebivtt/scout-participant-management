import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import pkg from './package.json' with { type: 'json' }

process.env.VITE_APP_VERSION = pkg.version
if (process.env.NODE_ENV === 'production') {
  process.env.VITE_APP_BUILD_EPOCH = new Date().getTime().toString()
}

// Den Schalter __VUE_PROD_HYDRATION_MISMATCH_DETAILS__ setzt
// @vitejs/plugin-vue seit Fassung 5 selbst (auf false), ein eigener
// `define`-Eintrag ist nicht mehr nötig. Die frühere Einstellung
// `esbuild.supported` für „top-level await“ kennt Vite 8 nicht mehr; mit
// `target: 'esnext'` darf der gebaute Code diese Sprachmittel ohnehin nutzen.
export default defineConfig({
  build: {
    // Neueste Sprachmittel nicht umschreiben: Das Tool richtet sich an
    // aktuelle Browser, und so bleibt der gebaute Code näher am Quelltext.
    target: 'esnext'
  },
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        'vue-router',
        '@vueuse/head',
        'pinia',
      ],
      dts: 'src/auto-imports.d.ts',
      eslintrc: {
        enabled: true,
      },
    }),
    Components({
      dirs: ['src/components'],
      extensions: ['vue'],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
