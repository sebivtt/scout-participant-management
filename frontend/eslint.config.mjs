// Code-Regeln für das Frontend (eslint 10).
//
// Bildet die frühere Einstellung aus `.eslintrc.js` (eslint 8) nach: dieselben
// Regelsätze für Vue 3, TypeScript und Sicherheit, Formatierungsregeln aus,
// dazu die eigenen Regeln unten. eslint 10 liest nur noch dieses Dateiformat.
// Allgemeine JavaScript-Regeln (`eslint:recommended`) waren nie eingeschaltet
// und bleiben aus, damit der Wechsel die Prüfung nicht nebenbei verschärft.
import { readFileSync } from 'node:fs'

import pluginVue from 'eslint-plugin-vue'
import pluginSecurity from 'eslint-plugin-security'
import prettierConfig from 'eslint-config-prettier/flat'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'

// Vite erzeugt diese Liste beim Bauen (unplugin-auto-import): Funktionen wie
// `ref` oder `computed`, die in jeder Datei ohne Import verfügbar sind.
const autoImportGlobals = JSON.parse(
  readFileSync(new URL('./.eslintrc-auto-import.json', import.meta.url), 'utf8'),
).globals

// Geprüft wird nur der Programmcode in `src/`, wie bisher: `yarn lint`
// ruft `eslint src` auf (früher `eslint --ext .ts,.vue src`).
export default defineConfigWithVueTs(
  pluginVue.configs['flat/recommended'],
  vueTsConfigs.recommended,
  pluginSecurity.configs.recommended,
  prettierConfig,
  {
    languageOptions: {
      globals: {
        ...autoImportGlobals,
        defineProps: 'readonly',
        defineEmits: 'readonly',
        defineExpose: 'readonly',
        withDefaults: 'readonly',
      },
    },
    rules: {
      // typescript-eslint 8 hat diese Regeln strenger eingestuft (Fehler statt
      // Warnung) oder aus seinem Standardsatz genommen. Sie stehen hier auf
      // der früheren Stufe: Sonst würden allein durch den Werkzeugwechsel rund
      // 1.500 Warnungen zu Fehlern. Schärfer gestellt wird später bewusst und
      // einzeln, wenn eslint Teil der automatischen Prüfung wird.
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': 'warn',
      '@typescript-eslint/no-non-null-assertion': 'warn',
      '@typescript-eslint/adjacent-overload-signatures': 'error',
      '@typescript-eslint/no-empty-function': 'error',
      '@typescript-eslint/no-inferrable-types': 'error',
      'no-var': 'error',
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'comma-dangle': ['error', 'only-multiline'],
    },
  },
)
