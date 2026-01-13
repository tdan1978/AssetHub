<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline" class="w-full justify-start text-left" type="button">
        <span v-if="modelValue">{{ modelValue }}</span>
        <span v-else class="text-muted-foreground">{{ placeholder }}</span>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-auto p-0" align="start">
      <Calendar
        v-model="selectedDate"
        :layout="showMonthYearSelect ? 'month-and-year' : undefined"
        :yearRange="yearRangeValues"
      />
    </PopoverContent>
  </Popover>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getLocalTimeZone, parseDate, today } from "@internationalized/date";
import { createYearRange } from "reka-ui/date";
import { Button } from "../button";
import { Calendar } from "../calendar";
import { Popover, PopoverContent, PopoverTrigger } from "../popover";

const props = defineProps({
  modelValue: {
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
</script>
