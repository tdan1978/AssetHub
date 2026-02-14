<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增报修</h2>
          <p class="text-sm text-muted-foreground">创建维修记录并自动将资产置为维修中。</p>
        </div>
        <RouterLink to="/maintenance">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">资产 ID / SN</label>
          <Input v-model="form.asset" placeholder="资产 ID / SN" />
        </div>
        <div class="form-field">
          <label class="form-label">问题描述</label>
          <Input v-model="form.issue" placeholder="问题描述" />
        </div>
        <div class="form-field">
          <label class="form-label">供应商</label>
          <Input v-model="form.vendor" placeholder="供应商" />
        </div>
        <div class="form-field">
          <label class="form-label">费用</label>
          <Input v-model="form.cost" placeholder="费用(可选)" />
        </div>
      </div>
      <div class="mt-4">
        <Button @click="save">提交报修</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

const router = useRouter();
const form = ref({ asset: "", issue: "", vendor: "", cost: "" });

const resolveAssetId = async (input) => {
  const value = String(input || "").trim();
  if (!value) return null;
  if (/^\d+$/.test(value)) return Number(value);
  const { data } = await api.get("/assets", { params: { page: 1, size: 1, q: value } });
  return data.items?.[0]?.id || null;
};

const save = async () => {
  const assetId = await resolveAssetId(form.value.asset);
  if (!assetId || !form.value.issue) return;
  await api.post("/maintenance/repairs", {
    asset_id: assetId,
    issue: form.value.issue,
    vendor: form.value.vendor || null,
    cost: form.value.cost || null
  });
  router.push("/maintenance");
};
</script>



