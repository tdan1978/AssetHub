<script setup>
import { computed } from "vue";
import { cn } from "@/lib/utils";

const props = defineProps({
  config: { type: Object, default: () => ({}) },
  class: { type: String, default: "" },
});

const style = computed(() => {
  const vars = {};
  const config = props.config || {};
  Object.keys(config).forEach((key) => {
    const item = config[key] || {};
    const color = item.color || item?.theme?.light || item?.theme?.dark;
    if (color) {
      vars[`--color-${key}`] = color;
    }
  });
  return vars;
});
</script>

<template>
  <div :class="cn('chart-container', props.class)" :style="style">
    <slot />
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
}
</style>

