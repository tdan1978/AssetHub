<template>
  <Popover>
    <PopoverTrigger as-child>
      <div class="relative w-full">
        <Button variant="outline" :class="['w-full justify-start text-left pr-9', props.class]" type="button">
          <span v-if="modelValue">{{ modelValue }}</span>
          <span v-else class="text-muted-foreground">{{ placeholder }}</span>
        </Button>
        <button
          v-if="modelValue"
          type="button"
          class="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-muted-foreground transition hover:text-foreground"
          aria-label="清除日期"
          @click.stop="clearValue"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0" align="start">
      <Calendar
        v-model="selectedDate"
        :layout="showMonthYearSelect ? 'month-and-year' : undefined"
        :yearRange="yearRangeValues"
        :locale="locale"
      />
    </PopoverContent>
  </Popover>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getLocalTimeZone, parseDate, today } from "@internationalized/date";
import { createYearRange } from "reka-ui/date";
import { X } from "lucide-vue-next";
import { Button } from "../button";
import { Calendar } from "../calendar";
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
  placeholder: {
    type: String,
    default: "选择日期"
  },
  showMonthYearSelect: {
    type: Boolean,
    default: false
  },
  yearRange: {
    type: Number,
    default: 10
  },
  locale: {
    type: String,
    default: "zh-CN"
  }
});

const emit = defineEmits(["update:modelValue"]);

const selectedDate = computed({
  get() {
    return props.modelValue ? parseDate(props.modelValue) : undefined;
  },
  set(value) {
    emit("update:modelValue", value ? value.toString() : "");
  }
});

const yearRangeValues = computed(() => {
  const base = today(getLocalTimeZone());
  return createYearRange({
    start: base.cycle("year", -props.yearRange),
    end: base.cycle("year", props.yearRange)
  });
});

const clearValue = () => {
  emit("update:modelValue", "");
};
</script>

