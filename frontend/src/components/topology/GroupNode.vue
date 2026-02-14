<template>
  <div class="group-node h-full w-full p-2" :style="groupStyle">
    <NodeResizer
      v-if="selected"
      :min-width="120"
      :min-height="80"
      :line-style="{ borderColor: '#16a34a' }"
      :handle-style="{ width: '8px', height: '8px', borderRadius: '9999px', border: '1px solid #16a34a', backgroundColor: '#ffffff' }"
    />
    <div class="pointer-events-none text-xs font-semibold text-foreground/80">
      {{ data?.label || "分组" }}
    </div>
    <Handle
      v-if="!data?.hideHandles"
      id="left"
      type="source"
      :position="Position.Left"
      class="!size-2.5 !border !border-background !bg-primary/70"
    />
    <Handle
      v-if="!data?.hideHandles"
      id="right"
      type="source"
      :position="Position.Right"
      class="!size-2.5 !border !border-background !bg-primary/70"
    />
    <Handle
      v-if="!data?.hideHandles"
      id="top"
      type="source"
      :position="Position.Top"
      class="!size-2.5 !border !border-background !bg-primary/70"
    />
    <Handle
      v-if="!data?.hideHandles"
      id="bottom"
      type="source"
      :position="Position.Bottom"
      class="!size-2.5 !border !border-background !bg-primary/70"
    />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { Handle, Position } from "@vue-flow/core";
import { NodeResizer } from "@vue-flow/node-resizer";

const props = defineProps({
  id: { type: String, required: true },
  data: { type: Object, default: () => ({}) },
  selected: { type: Boolean, default: false },
});

const groupStyle = computed(() => {
  const radius = Math.max(0, Math.min(80, Number(props.data?.borderRadius ?? 12)));
  return {
    borderRadius: `${radius}px`,
    border: `1px dashed ${props.data?.borderColor || "#cbd5e1"}`,
    backgroundColor: props.data?.bgColor || "#e2e8f0",
    boxSizing: "border-box",
  };
});
</script>

