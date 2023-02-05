<template>
  <PageWrapper>
    <MyTabGroup :tabs="tabs" />
  </PageWrapper>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import MyTabGroup from "@/components/menu/TabGroup.vue";
import PageWrapper from "@/components/base/PageWrapper.vue";

const route = useRoute();

const tabs = computed(() => {
  return [
    {
      name: "Neue Nachrichten",
      linkName: "NewMessages",
      current: route.name === "NewMessages",
    },
    {
      name: "Alle Nachrichten",
      linkName: "AllMessages",
      current: route.name === "AllMessages",
    },
  ];
});
</script>
