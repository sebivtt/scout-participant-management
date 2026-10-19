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

// Bewusst ohne eigene Sprachziele für Pakete im Entwicklungsmodus
// (optimizeDeps): Vite 8 wählt dort eine Grundlinie aktueller Browser, und
// keines unserer Pakete nutzt Sprachmittel darüber hinaus, etwa „top-level
// await“ (geprüft beim Update auf Vite 8, Oktober 2026). Kommt ein solches
// Paket hinzu, hier unter `optimizeDeps` ein passendes Ziel einstellen.
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
