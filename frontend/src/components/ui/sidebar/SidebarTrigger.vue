<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { cn } from "@/lib/utils"

const props = defineProps<{ class?: HTMLAttributes["class"] }>()
</script>

<template>
  <button
    type="button"
    :class="
      cn(
        'inline-flex size-8 items-center justify-center rounded-md border bg-background text-muted-foreground shadow-xs transition hover:text-foreground',
        props.class,
      )
    "
  >
    <slot />
  </button>
</template>
