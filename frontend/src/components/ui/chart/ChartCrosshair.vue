<script setup>
import { VisCrosshair } from "@unovis/vue";

const props = defineProps({
  template: { type: Function, default: null },
  color: { type: String, default: "var(--muted-foreground)" },
  strokeColor: { type: String, default: "var(--background)" },
  strokeWidth: { type: Number, default: 2 },
  snapToData: { type: Boolean, default: true },
  hideWhenFarFromPointer: { type: Boolean, default: true },
});
</script>

<template>
  <VisCrosshair v-bind="props" />
</template>

