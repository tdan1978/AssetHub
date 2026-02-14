<template>
  <div class="inline-flex flex-wrap gap-2">
    <slot />
  </div>
</template>

<script setup>
import { computed, provide } from "vue";

const props = defineProps({
  modelValue: { type: [Array, String], default: () => [] },
  type: { type: String, default: "single" }
});

const emit = defineEmits(["update:modelValue"]);

const currentValues = computed(() => {
  if (props.type === "multiple") {
    return Array.isArray(props.modelValue) ? props.modelValue : [];
  }
  return props.modelValue ? [props.modelValue] : [];
});

const toggleValue = (value) => {
  if (props.type === "multiple") {
    const next = new Set(currentValues.value);
    if (next.has(value)) {
      next.delete(value);
    } else {
      next.add(value);
    }
    emit("update:modelValue", Array.from(next));
  } else {
    emit("update:modelValue", value);
  }
};

const isActive = (value) => currentValues.value.includes(value);

provide("toggleGroupContext", {
  type: props.type,
  toggleValue,
  isActive
});
</script>

