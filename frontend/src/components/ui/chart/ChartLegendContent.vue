<script setup>
const props = defineProps({
  items: { type: Array, default: () => [] },
});
</script>

<template>
  <div class="chart-legend">
    <div v-for="item in items" :key="item.label" class="chart-legend-row">
      <span class="chart-legend-dot" :style="{ background: item.color }"></span>
      <span class="chart-legend-label">{{ item.label }}</span>
      <span class="chart-legend-value">{{ item.value }}</span>
    </div>
  </div>
</template>

<style scoped>
.chart-legend {
  display: grid;
  gap: 6px;
}

.chart-legend-row {
  display: grid;
  grid-template-columns: 10px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--muted-foreground);
}

.chart-legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.chart-legend-label {
  color: var(--muted-foreground);
}

.chart-legend-value {
  font-weight: 600;
  color: var(--foreground);
}
</style>

