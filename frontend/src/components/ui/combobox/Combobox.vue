<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button variant="outline" :class="['w-full justify-between', props.class]" type="button">
        <span v-if="modelValue">{{ selectedLabel || modelValue }}</span>
        <span v-else class="text-muted-foreground">{{ placeholder }}</span>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-full p-2" align="start">
      <Input
        v-model="query"
        class="h-8"
        placeholder="搜索..."
        @keydown.stop
      />
      <div class="mt-2 max-h-52 overflow-auto rounded-md border bg-background">
        <button
          v-for="option in filteredOptions"
          :key="option.value"
          type="button"
          class="flex w-full items-center justify-between px-3 py-2 text-sm hover:bg-muted"
          @click="selectOption(option.value)"
        >
          <span>{{ option.label }}</span>
          <Check v-if="option.value === modelValue" class="h-4 w-4 text-primary" />
        </button>
        <div v-if="!filteredOptions.length" class="px-3 py-2 text-sm text-muted-foreground">
          无匹配项
        </div>
      </div>
    </PopoverContent>
  </Popover>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { Check } from "lucide-vue-next";
import { Button } from "../button";
import { Input } from "../input";
import { Popover, PopoverContent, PopoverTrigger } from "../popover";

const props = defineProps({
  modelValue: {
    type: String,
    default: ""
  },
  class: {
    type: String,
    default: ""
  },
  options: {
    type: Array as () => Array<{ label: string; value: string } | string>,
    default: () => []
  },
  placeholder: {
    type: String,
    default: "请选择"
  }
});

const emit = defineEmits(["update:modelValue"]);

const open = ref(false);
const query = ref("");

const normalizedOptions = computed(() =>
  (props.options || []).map((item) =>
    typeof item === "string" ? { label: item, value: item } : item
  )
);

const selectedLabel = computed(() => {
  const match = normalizedOptions.value.find((item) => item.value === props.modelValue);
  return match?.label || "";
});

const filteredOptions = computed(() => {
  if (!query.value) return normalizedOptions.value;
  const q = query.value.toLowerCase();
  return normalizedOptions.value.filter((item) => item.label.toLowerCase().includes(q));
});

const selectOption = (value: string) => {
  emit("update:modelValue", value);
  open.value = false;
};

watch(open, (value) => {
  if (!value) {
    query.value = "";
  }
});
</script>

