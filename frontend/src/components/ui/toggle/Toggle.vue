<template>
  <button
    type="button"
    class="inline-flex items-center justify-center rounded-md border px-3 py-1 text-sm transition-colors"
    :class="[
      modelValue ? 'bg-primary text-primary-foreground border-primary' : 'bg-background text-foreground',
      disabled ? 'opacity-50 pointer-events-none' : 'hover:bg-muted'
    ]"
    :disabled="disabled"
    @click="toggle"
  >
    <slot />
  </button>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }
});

const emit = defineEmits(["update:modelValue"]);

const toggle = () => {
  emit("update:modelValue", !props.modelValue);
};
</script>

