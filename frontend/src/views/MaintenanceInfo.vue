<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">维保信息</h2>
          <p class="text-sm text-muted-foreground">按资产维护维保合同与厂家信息。</p>
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
          <label class="form-label">维保合同号</label>
          <Input v-model="form.contract_no" placeholder="维保合同号" />
        </div>
        <div class="form-field">
          <label class="form-label">厂家报修电话</label>
          <Input v-model="form.support_phone" placeholder="厂家报修电话" />
        </div>
        <div class="form-field">
          <label class="form-label">供应商</label>
          <Input v-model="form.vendor" placeholder="供应商" />
        </div>
        <div class="form-field">
          <label class="form-label">维保到期日</label>
          <DatePicker v-model="form.warranty_at" placeholder="维保到期日" :showMonthYearSelect="true" />
        </div>
      </div>
      <div class="mt-4 flex gap-2">
        <Button variant="outline" @click="loadInfo">加载</Button>
        <Button @click="saveInfo">保存</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { DatePicker } from "../components/ui/date-picker";

const form = ref({ asset: "", contract_no: "", support_phone: "", vendor: "", warranty_at: "" });

const resolveAssetId = async (input) => {
  const value = String(input || "").trim();
  if (!value) return null;
  if (/^\d+$/.test(value)) return Number(value);
  const { data } = await api.get("/assets", { params: { page: 1, size: 1, q: value } });
  return data.items?.[0]?.id || null;
};

const loadInfo = async () => {
  const assetId = await resolveAssetId(form.value.asset);
  if (!assetId) return;
  const { data } = await api.get(`/maintenance/info/${assetId}`);
  form.value = {
    asset: form.value.asset,
    contract_no: data.contract_no || "",
    support_phone: data.support_phone || "",
    vendor: data.vendor || "",
    warranty_at: data.warranty_at || ""
  };
};

const saveInfo = async () => {
  const assetId = await resolveAssetId(form.value.asset);
  if (!assetId) return;
  await api.put(`/maintenance/info/${assetId}`, {
    contract_no: form.value.contract_no || null,
    support_phone: form.value.support_phone || null,
    vendor: form.value.vendor || null,
    warranty_at: form.value.warranty_at || null
  });
};
</script>
