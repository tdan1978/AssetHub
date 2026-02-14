<template>
  <div
    class="editable-node rounded-md border px-3 py-2 shadow-sm transition select-none"
    :class="[selectedClass, nodeCursorClass, editing ? 'select-text' : 'select-none']"
    :style="nodeStyle"
    @dblclick.stop="startEdit"
  >
    <NodeResizer
      v-if="selected && !isTextNode"
      :min-width="80"
      :min-height="40"
      :max-width="420"
      :max-height="260"
      :line-style="{ borderColor: '#16a34a' }"
      :handle-style="{ width: '8px', height: '8px', borderRadius: '9999px', border: '1px solid #16a34a', backgroundColor: '#ffffff' }"
    />
    <Handle
      v-if="!data?.hideHandles && !isTextNode"
      id="left"
      type="source"
      :position="Position.Left"
      class="!size-2.5 !border !border-background !bg-primary"
    />
    <Handle
      v-if="!data?.hideHandles && !isTextNode"
      id="right"
      type="source"
      :position="Position.Right"
      class="!size-2.5 !border !border-background !bg-primary"
    />
    <Handle
      v-if="!data?.hideHandles && !isTextNode"
      id="top"
      type="source"
      :position="Position.Top"
      class="!size-2.5 !border !border-background !bg-primary"
    />
    <Handle
      v-if="!data?.hideHandles && !isTextNode"
      id="bottom"
      type="source"
      :position="Position.Bottom"
      class="!size-2.5 !border !border-background !bg-primary"
    />
    <div class="flex w-full min-h-[1.1rem]" :class="labelContainerClass">
      <div class="inline-flex max-w-full items-center gap-1.5">
        <component
          :is="iconComponent"
          v-if="iconComponent"
          class="size-3.5 shrink-0"
          :style="{ color: data?.textColor || '#0f172a' }"
        />
        <div
          ref="labelEl"
          class="min-w-[2ch] min-h-[1.2em] whitespace-pre-wrap break-words outline-none"
          :class="labelCursorClass"
          :style="labelStyle"
          :contenteditable="editing && canEditLabel ? 'true' : null"
          spellcheck="false"
          @input="onInput"
          @dblclick.stop="startEdit"
          @blur="finishEdit"
          @keydown.enter.prevent="finishEdit"
          @mousedown="onLabelMouseDown"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { Handle, Position } from "@vue-flow/core";
import { NodeResizer } from "@vue-flow/node-resizer";
import { TOPOLOGY_ICON_COMPONENTS } from "./icon-options";

const props = defineProps({
  id: { type: String, required: true },
  data: { type: Object, default: () => ({}) },
  selected: { type: Boolean, default: false },
});

const labelEl = ref(null);
const editing = ref(false);
const iconComponent = computed(() => TOPOLOGY_ICON_COMPONENTS[String(props.data?.icon || "").trim()] || null);
const isTextNode = computed(() => String(props.data?.nodeKind || "") === "text");
const isSystemNode = computed(() => String(props.data?.nodeKind || "") === "system");
const canEditLabel = computed(() => !isSystemNode.value);
const nodeCursorClass = computed(() => (editing.value ? "cursor-text" : "cursor-move"));
const labelCursorClass = computed(() => {
  if (editing.value) return "cursor-text";
  if (canEditLabel.value) return "cursor-text";
  return "cursor-move";
});
const selectedClass = computed(() => {
  if (!props.selected) return "";
  return isTextNode.value ? "ring-1 ring-primary/40" : "ring-2 ring-primary/30";
});

const clamp = (val, min, max) => Math.min(max, Math.max(min, val));

const nodeStyle = computed(() => {
  const width = clamp(Number(props.data?.width || 120), 80, 420);
  const height = clamp(Number(props.data?.height || 48), 40, 260);
  const borderRadius = clamp(Number(props.data?.borderRadius ?? 10), 0, 60);
  const verticalAlign = String(props.data?.verticalAlign || "center");
  const alignItems = verticalAlign === "top" ? "flex-start" : verticalAlign === "bottom" ? "flex-end" : "center";
  if (isTextNode.value) {
    const maxWidth = clamp(Number(props.data?.width || 360), 120, 720);
    return {
      width: "fit-content",
      minHeight: "20px",
      height: "auto",
      minWidth: "20px",
      maxWidth: `${maxWidth}px`,
      padding: "4px 6px",
      margin: "0",
      backgroundColor: "transparent",
      border: "1px dashed #94a3b8",
      borderWidth: "1px",
      borderRadius: "0",
      boxShadow: "none",
      boxSizing: "border-box",
      display: "flex",
      alignItems,
    };
  }
  return {
    width: `${width}px`,
    minHeight: `${height}px`,
    height: `${height}px`,
    backgroundColor: props.data?.bgColor || "#ffffff",
    borderColor: props.data?.borderColor || "#cbd5e1",
    borderWidth: "1px",
    borderStyle: "solid",
    borderRadius: `${borderRadius}px`,
    boxSizing: "border-box",
    display: "flex",
    alignItems,
  };
});

const textAlign = computed(() => {
  const align = String(props.data?.textAlign || "center");
  return align === "left" || align === "right" ? align : "center";
});

const labelContainerClass = computed(() => {
  if (textAlign.value === "left") return "justify-start";
  if (textAlign.value === "right") return "justify-end";
  return "justify-center";
});

const labelStyle = computed(() => ({
  color: props.data?.textColor || "#0f172a",
  textAlign: textAlign.value,
  fontSize: `${Math.min(40, Math.max(10, Number(props.data?.fontSize || 14)))}px`,
  lineHeight: isTextNode.value ? "1.35" : "1",
  fontWeight: isTextNode.value ? 500 : 600,
}));

const setLabel = () => {
  if (!labelEl.value) return;
  // Keep caret stable while typing.
  if (editing.value && document.activeElement === labelEl.value) return;
  const next = String(props.data?.label || "");
  if (labelEl.value.innerText !== next) {
    labelEl.value.innerText = next;
  }
};

watch(() => props.data?.label, setLabel, { immediate: true });
onMounted(setLabel);

const onInput = (event) => {
  if (!canEditLabel.value) {
    setLabel();
    return;
  }
  const next = String(event.target?.innerText || "");
  // Vue Flow node.data is a mutable object; write-through keeps the canvas reactive.
  props.data.label = next;
};

const startEdit = async () => {
  if (!canEditLabel.value) return;
  editing.value = true;
  await nextTick();
  if (!labelEl.value) return;
  labelEl.value.focus();
  const range = document.createRange();
  range.selectNodeContents(labelEl.value);
  range.collapse(false);
  const selection = window.getSelection();
  selection?.removeAllRanges();
  selection?.addRange(range);
};

const finishEdit = () => {
  editing.value = false;
  const next = String(labelEl.value?.innerText || "");
  props.data.label = next;
};

const onLabelMouseDown = (event) => {
  if (canEditLabel.value) {
    event.stopPropagation();
    return;
  }
  if (!editing.value) return;
  event.stopPropagation();
};
</script>

