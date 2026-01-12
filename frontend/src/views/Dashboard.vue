<template>
  <div>
    <div class="mb-6 flex flex-col gap-3 rounded-lg border bg-background p-5 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-xl font-semibold">资产态势总览</h1>
        <p class="text-sm text-muted-foreground">掌握 IT 资产全生命周期数据</p>
      </div>
      <Button @click="refresh">刷新数据</Button>
    </div>

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      <div class="card">
        <div class="label">总资产</div>
        <div class="value">{{ data.total }}</div>
      </div>
      <div class="card">
        <div class="label">在用率</div>
        <div class="value">{{ (data.in_use_rate * 100).toFixed(1) }}%</div>
      </div>
      <div class="card">
        <div class="label">待维修</div>
        <div class="value">{{ data.repairing }}</div>
      </div>
      <div class="card">
        <div class="label">待报废</div>
        <div class="value">{{ data.pending_scrap }}</div>
      </div>
      <div class="card">
        <div class="label">软件到期预警</div>
        <div class="value">{{ data.license_expire_warn }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";

const data = ref({
  total: 0,
  in_use_rate: 0,
  repairing: 0,
  pending_scrap: 0,
  license_expire_warn: 0
});

const refresh = async () => {
  const res = await api.get("/dashboard");
  data.value = res.data;
};

onMounted(refresh);
</script>

<style scoped>
.card {
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card);
  padding: 16px;
}

.label {
  font-size: 12px;
  color: var(--muted-foreground);
}

.value {
  margin-top: 6px;
  font-size: 24px;
  font-weight: 600;
}
</style>
