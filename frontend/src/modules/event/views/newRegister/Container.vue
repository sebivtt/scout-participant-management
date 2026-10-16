<template>
  <PageWrapper class="mt-12 sm:mt-0">
    <div class="lg:border-t lg:border-b lg:border-gray-200">
      <nav
        class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 md:py-8"
        aria-label="Progress"
      >
        <component :is="components[compNo]" :steps="steps" />
      </nav>
      <router-view
        :step="
          steps.find((step) => {
            return step.current;
          })
        "
      />
    </div>
  </PageWrapper>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";

import StepperNavSmall from "@/components/stepper/StepperNavSmall.vue";
import PageWrapper from "@/components/base/PageWrapper.vue";
import { useRouter } from "vue-router";
import { useEventStore } from "@/modules/event/store/index";
import { onBeforeRouteLeave } from "vue-router";
import { useRoute } from "vue-router";
const route = useRoute();

const router = useRouter();

const eventStore = useEventStore();

const components = [StepperNavSmall, StepperNavSmall];

const compNo = computed(() => {
  return window.innerWidth < 1200 ? 0 : 1;
});

// Schritte mit eigener Seite im Anmeldeablauf (siehe router/index.ts). Alle
// anderen, z. B. „Tshirts“ und „LunchMeals“ aus der Standardvorlage, zeigt die
// allgemeine Seite für Zusatzfelder (Custom) anhand ihrer Kennung. Bis Issue #25
// lief „weiter“ bei solchen Schritten ins Leere, weil es keine Seite
// „RegistrationTshirts“ gibt.
const STEPS_WITH_OWN_PAGE = ["Introduction", "Participants", "Travel", "TravelBack", "Letter", "Custom", "Summary"];

/** Name der Seite, die einen Schritt im Anmeldeablauf anzeigt. */
function stepLink(eventModule: any): string {
  const name = STEPS_WITH_OWN_PAGE.includes(eventModule.name) ? eventModule.name : "Custom";
  return `Registration${name}`;
}

function nextLink(eventModule: any) {
  try {
    return getCompLeftList(eventModule.id)[0].link;
  } catch (error) {
    return "Custom";
  }
}

function nextId(eventModule) {
  try {
    return getCompLeftList(eventModule.id)[0].id;
  } catch (error) {
    return 1;
  }
}

const steps = computed(() => {
  const eventObj: any = [];
  eventModuleList.value.forEach((eventModule: any) => {
    const compName = stepLink(eventModule);
    const routeObj = {
      id: eventModule.id,
      name: eventModule.name,
      header: eventModule.header,
      description: eventModule.description,
      link: compName,
      nextLink: nextLink(eventModule),
      nextId: nextId(eventModule),
      status: getStatus(eventModule, eventModuleList.value),
      current: getCurrent(eventModule, eventModule.id),
    };
    console.log(routeObj);
    eventObj.push(routeObj);
  });
  return eventObj;
});

function getStatus(eventModule, eventModules) {
  const currentId = parseInt(router.currentRoute.value.params.module, 10);

  const eventModuleIndexes = eventModules.map((module) => module.id);

  const indexTemp = eventModuleIndexes.indexOf(eventModule.id);
  const indexCurrent = eventModuleIndexes.indexOf(currentId);

  let status = "";

  status = indexTemp > indexCurrent ? status : "complete";
  status = indexTemp === indexCurrent ? "current" : status;

  return status;
}

/**
 * Ist dieser Schritt gerade geöffnet?
 *
 * Die Seite für Zusatzfelder zeigt mehrere Schritte, deshalb zählt dort
 * zusätzlich die Kennung in der Adresse.
 */
function getCurrent(eventModule: any, index: any) {
  const compName = stepLink(eventModule);
  return (
    router.currentRoute.value.name == compName &&
    (router.currentRoute.value.params.module == index ||
      compName !== "RegistrationCustom")
  );
}

const event = computed(() => {
  return eventStore.event;
});

const isLoading = computed(() => {
  return eventStore.isLoading;
});

const eventModuleList = computed(() => {
  if (
    eventStore.event?.eventmoduleSet &&
    eventStore.event?.eventmoduleSet.length
  ) {
    return eventStore.event.eventmoduleSet;
  }
  return [];
});

function getCompLeftList(id) {
  const moduleList = eventModuleList.value;
  const compList = moduleList.map((module: any) => {
    return {
      link: stepLink(module),
      id: module.id,
    };
  });
  const index = compList.map((item) => item.id).indexOf(id);
  return compList.slice(index + 1);
}

function getCompLeftListIndex(ind: any) {
  const moduleList = eventModuleList.value;
  const compList = moduleList.map((module) => module.id);
  const index = compList.indexOf(ind);
  return compList.slice(index + 1);
}

onMounted(() => {
  eventStore.fetchAllMappings();
  const id = route.params.id;
  if (id) {
    eventStore.fetchEvent(id);
  }
});

onBeforeRouteLeave((to, from) => {
  // if (eventStore.registered) {
  //   eventStore.reset();
  //   return true;
  // }
  // const exit = window.confirm(
  //   "Wenn du den Registrierungsprozess verlässt, werden deine Eingaben aus Sicherheitsgründen gelöscht. Möchtest du fortfahren?"
  // );
  // if (exit) {
  //   eventStore.reset();
  //   return true;
  // } else {
  //   return false;
  // }
});
</script>
