<template>
  <div :class="`sm:col-span-${props.cols}`">
    <label class="block text-sm font-medium text-gray-700">{{
      props.label
    }}</label>
    <div class="relative mt-1 rounded-md shadow-sm">
      <QuillEditor
        theme="snow"
        :toolbar="toolbarOptions"
        @ready="onReady"
        @text-change="onTextChange"
      />
      <div
        v-if="hasError"
        class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3"
      >
        <ExclamationCircleIcon
          class="h-5 w-5 text-red-500"
          aria-hidden="true"
        />
      </div>
    </div>
    <p class="mt-2 text-sm text-red-500" id="email-description">
      {{ props.errors[0] && props.errors[0].$message }}
    </p>
    <p
      v-if="props.hint"
      class="mt-2 text-sm text-gray-500"
      id="email-description"
    >
      {{ props.hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

import { ExclamationCircleIcon } from "@heroicons/vue/20/solid";

const toolbarOptions = ref('essential')

const props = defineProps({
  modelValue: { type: String, required: true },
  errors: { type: Array, required: false, default: () => [] },
  label: { type: String, required: true },
  hint: { type: String, required: false, default: "" },
  cols: { type: Number, required: false, default: 3 },
});

const emit = defineEmits(["update:modelValue"]);

const hasError = computed(() => {
  return props.errors[0] && props.errors.length;
});

// Der Text wird bewusst nicht über `contentType="html"` von vue-quill
// gelesen und geschrieben. vue-quill nimmt dafür das rohe HTML des
// Editors (`innerHTML`). Seit Quill 2 ist das ein eigenes Format: Eine
// Aufzählung steht dort als nummerierte Liste mit dem Vermerk
// `data-list="bullet"`, und gewöhnliches HTML wie `<ul><li>` verschwindet
// beim Laden ganz. Überall außerhalb des Editors (Einladung, Anmeldeablauf)
// erschiene eine Aufzählung dann nummeriert, und gespeicherte Listen gingen
// beim erneuten Öffnen verloren.
let quill = null;
// Zuletzt selbst gemeldeter Text. So lässt sich unterscheiden, ob ein neuer
// `modelValue` aus dem eigenen Tippen stammt oder von außen kommt (z. B.
// wenn das Formular die gespeicherten Daten erst nach dem Öffnen lädt).
let lastEmitted = null;

/**
 * Lädt gewöhnliches HTML in den Editor. Quills eigene Umwandlung
 * (`clipboard.convert`) übersetzt Listen und Formatierungen in sein
 * internes Format. „silent“ verhindert, dass das Laden als Änderung gilt.
 */
function loadHtml(html) {
  lastEmitted = html;
  quill.setContents(quill.clipboard.convert({ html: html || "" }), "silent");
}

/** Übernimmt den Editor, sobald vue-quill Quill geladen hat. */
function onReady(instance) {
  quill = instance;
  loadHtml(props.modelValue);
}

/**
 * Meldet jede Änderung als gewöhnliches HTML (`getSemanticHTML`), damit
 * Listen auch außerhalb des Editors richtig angezeigt werden.
 */
function onTextChange() {
  lastEmitted = quill.getSemanticHTML();
  emit("update:modelValue", lastEmitted);
}

watch(
  () => props.modelValue,
  (value) => {
    if (quill && value !== lastEmitted) {
      loadHtml(value);
    }
  },
);

</script>
