<script setup>
import { VisTooltip } from "@unovis/vue";

const props = defineProps({
  triggers: { type: Object, default: () => ({}) },
  container: { type: Object, default: null },
  followCursor: { type: Boolean, default: true },
  allowHover: { type: Boolean, default: false },
  className: { type: String, default: "chart-tooltip-root" },
});
</script>

<template>
  <VisTooltip v-bind="props" />
</template>

