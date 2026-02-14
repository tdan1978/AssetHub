<script setup lang="ts">
import type { HTMLAttributes } from "vue"
import { cn } from "@/lib/utils"

const props = defineProps<{
  class?: HTMLAttributes["class"]
  collapsed?: boolean
}>()
</script>

<template>
  <aside
    :data-collapsed="props.collapsed ? 'true' : 'false'"
    :class="
      cn(
        'group/sidebar flex h-screen flex-col border-r bg-background text-foreground transition-[width] duration-200',
        props.collapsed ? 'w-16' : 'w-72',
        props.class,
      )
    "
  >
    <slot />
  </aside>
</template>

