<template>
  <button
    type="button"
    class="inline-flex items-center justify-center gap-1 rounded-md border px-3 py-1 text-sm transition-colors"
    :class="[
      active
        ? 'bg-primary text-primary-foreground border-primary'
        : props.mutedWhenInactive
          ? 'bg-muted text-muted-foreground border-muted-foreground/20'
          : 'bg-background text-foreground',
      disabled ? 'opacity-50 pointer-events-none' : active ? 'hover:bg-primary' : 'hover:bg-muted'
    ]"
    :disabled="disabled"
    @click="handleClick"
  >
    <span v-if="showCheck" class="inline-flex h-3 w-3 items-center justify-center">
      <Check v-if="active" class="h-3 w-3" />
      <span v-else-if="props.inactiveDot" class="h-1.5 w-1.5 rounded-full bg-current opacity-60" />
    </span>
    <slot />
  </button>
</template>

<script setup>
import { computed, inject } from "vue";
import { Check } from "lucide-vue-next";

const props = defineProps({
  value: { type: String, required: true },
  disabled: { type: Boolean, default: false },
  showCheck: { type: Boolean, default: false },
  mutedWhenInactive: { type: Boolean, default: false },
  inactiveDot: { type: Boolean, default: false }
});

const ctx = inject("toggleGroupContext", null);

const active = computed(() => (ctx ? ctx.isActive(props.value) : false));

const handleClick = () => {
  if (ctx) {
    ctx.toggleValue(props.value);
  }
};
</script>

