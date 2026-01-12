<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">维保与报修</h2>
      <p class="mt-1 text-sm text-muted-foreground">记录供应商、维保合同与维修费用，形成资产持有成本。</p>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="card">
        <h3 class="text-sm font-semibold">新增报修</h3>
        <div class="mt-3 grid gap-2">
          <input v-model="repairForm.asset" class="input" placeholder="资产 ID / SN" />
          <input v-model="repairForm.issue" class="input" placeholder="问题描述" />
          <input v-model="repairForm.vendor" class="input" placeholder="供应商" />
          <input v-model="repairForm.cost" class="input" placeholder="费用(可选)" />
          <Button @click="createRepair">提交报修</Button>
        </div>
      </div>
      <div class="card">
        <h3 class="text-sm font-semibold">维保信息</h3>
        <div class="mt-3 grid gap-2">
          <input v-model="infoForm.asset" class="input" placeholder="资产 ID / SN" />
          <input v-model="infoForm.contract_no" class="input" placeholder="维保合同号" />
          <input v-model="infoForm.support_phone" class="input" placeholder="厂家报修电话" />
          <input v-model="infoForm.vendor" class="input" placeholder="供应商" />
          <input v-model="infoForm.warranty_at" class="input" placeholder="维保到期日(YYYY-MM-DD)" />
          <div class="flex gap-2">
            <Button variant="outline" @click="loadInfo">加载信息</Button>
            <Button variant="outline" @click="saveInfo">保存信息</Button>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">维修记录</h3>
      <table class="table mt-3">
        <thead>
          <tr>
            <th>资产</th>
            <th>故障</th>
            <th>费用</th>
            <th>状态</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in repairs" :key="item.id">
            <td>{{ item.asset_id }}</td>
            <td>{{ item.issue }}</td>
            <td>{{ item.cost || "-" }}</td>
            <td>{{ item.status }}</td>
            <td>{{ item.created_at || "-" }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { Button } from "../components/ui/button";
import { onMounted, ref } from "vue";
import api from "../api/client";

const repairs = ref([]);
const repairForm = ref({ asset: "", issue: "", vendor: "", cost: "" });
const infoForm = ref({ asset: "", contract_no: "", support_phone: "", vendor: "", warranty_at: "" });

const resolveAssetId = async (input) => {
  const value = String(input || "").trim();
  if (!value) return null;
  if (/^\d+$/.test(value)) return Number(value);
  const { data } = await api.get("/assets", { params: { page: 1, size: 1, q: value } });
  return data.items?.[0]?.id || null;
};

const loadRepairs = async () => {
  const { data } = await api.get("/maintenance/repairs");
  repairs.value = data;
};

const createRepair = async () => {
  const assetId = await resolveAssetId(repairForm.value.asset);
  if (!assetId || !repairForm.value.issue) return;
  await api.post("/maintenance/repairs", {
    asset_id: assetId,
    issue: repairForm.value.issue,
    vendor: repairForm.value.vendor || null,
    cost: repairForm.value.cost || null
  });
  repairForm.value = { asset: "", issue: "", vendor: "", cost: "" };
  await loadRepairs();
};

const loadInfo = async () => {
  const assetId = await resolveAssetId(infoForm.value.asset);
  if (!assetId) return;
  const { data } = await api.get(`/maintenance/info/${assetId}`);
  infoForm.value = {
    asset: infoForm.value.asset,
    contract_no: data.contract_no || "",
    support_phone: data.support_phone || "",
    vendor: data.vendor || "",
    warranty_at: data.warranty_at || ""
  };
};

const saveInfo = async () => {
  const assetId = await resolveAssetId(infoForm.value.asset);
  if (!assetId) return;
  await api.put(`/maintenance/info/${assetId}`, {
    contract_no: infoForm.value.contract_no || null,
    support_phone: infoForm.value.support_phone || null,
    vendor: infoForm.value.vendor || null,
    warranty_at: infoForm.value.warranty_at || null
  });
};

onMounted(loadRepairs);
</script>

<style scoped></style>
