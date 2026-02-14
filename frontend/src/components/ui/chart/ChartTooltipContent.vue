<script setup>
const props = defineProps({
  title: { type: String, default: "" },
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <div class="chart-tooltip">
    <div v-if="title" class="chart-tooltip-title">{{ title }}</div>
    <div class="chart-tooltip-items">
      <div v-for="(item, idx) in items" :key="`${item.label || 'item'}-${idx}`" class="chart-tooltip-row">
        <span class="chart-tooltip-dot" :style="{ background: item.color }"></span>
        <span class="chart-tooltip-label">{{ item.label }}</span>
        <span class="chart-tooltip-value">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-tooltip {
  min-width: 120px;
  border-radius: 6px;
  border: none;
  background: var(--popover);
  color: var(--popover-foreground);
  padding: 6px 8px;
  box-shadow: none;
}

.chart-tooltip-title {
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 4px;
}

.chart-tooltip-items {
  display: grid;
  gap: 2px;
}

.chart-tooltip-row {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: var(--muted-foreground);
}

.chart-tooltip-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
}

.chart-tooltip-label {
  color: var(--muted-foreground);
}

.chart-tooltip-value {
  font-weight: 600;
  color: var(--foreground);
}
</style>

