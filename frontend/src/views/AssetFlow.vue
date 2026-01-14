<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">资产流转操作</h2>
      <p class="mt-1 text-sm text-muted-foreground">领用、退库、调拨需符合资产状态流转规则。</p>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <div class="card">
        <h3 class="text-sm font-semibold">领用</h3>
        <div class="mt-3 grid gap-3">
          <div class="form-field">
            <label class="form-label">资产 ID / SN</label>
            <Input v-model="checkout.asset" placeholder="资产 ID / SN" />
          </div>
          <div class="form-field">
            <label class="form-label">领用人 ID</label>
            <Input v-model="checkout.user_id" placeholder="领用人 ID" />
          </div>
          <div class="form-field">
            <label class="form-label">部门</label>
            <Input v-model="checkout.dept" placeholder="部门" />
          </div>
          <Button @click="submitCheckout">提交领用</Button>
        </div>
      </div>

      <div class="card">
        <h3 class="text-sm font-semibold">退库</h3>
        <div class="mt-3 grid gap-3">
          <div class="form-field">
            <label class="form-label">资产 ID / SN</label>
            <Input v-model="checkin.asset" placeholder="资产 ID / SN" />
          </div>
          <div class="form-field">
            <label class="form-label">设备状况</label>
            <Select v-model="checkin.damaged">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="设备状况" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="false">设备状况：完好</SelectItem>
                <SelectItem value="true">设备状况：损坏</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button @click="submitCheckin">提交退库</Button>
        </div>
      </div>

      <div class="card">
        <h3 class="text-sm font-semibold">调拨</h3>
        <div class="mt-3 grid gap-3">
          <div class="form-field">
            <label class="form-label">资产 ID / SN</label>
            <Input v-model="transfer.asset" placeholder="资产 ID / SN" />
          </div>
          <div class="form-field">
            <label class="form-label">目标部门</label>
            <Input v-model="transfer.dept" placeholder="目标部门" />
          </div>
          <Button @click="submitTransfer">提交调拨</Button>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">操作结果</h3>
      <p class="mt-2 text-sm text-muted-foreground">{{ message || "等待操作" }}</p>
    </div>
  </div>
</template>

<script setup>
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { ref } from "vue";
import api from "../api/client";

const message = ref("");
const checkout = ref({ asset: "", user_id: "", dept: "" });
const checkin = ref({ asset: "", damaged: "false" });
const transfer = ref({ asset: "", dept: "" });

const resolveAssetId = async (input) => {
  const value = String(input || "").trim();
  if (!value) return null;
  if (/^\d+$/.test(value)) return Number(value);
  const { data } = await api.get("/assets", { params: { page: 1, size: 1, q: value } });
  return data.items?.[0]?.id || null;
};

const submitCheckout = async () => {
  message.value = "";
  try {
    const assetId = await resolveAssetId(checkout.value.asset);
    if (!assetId) {
      message.value = "找不到资产，请确认输入。";
      return;
    }
    await api.post(`/assets/${assetId}/checkout`, null, {
      params: { user_id: checkout.value.user_id, dept: checkout.value.dept }
    });
    message.value = "领用成功";
  } catch (err) {
    message.value = "领用失败，请检查资产状态或参数。";
  }
};

const submitCheckin = async () => {
  message.value = "";
  try {
    const assetId = await resolveAssetId(checkin.value.asset);
    if (!assetId) {
      message.value = "找不到资产，请确认输入。";
      return;
    }
    await api.post(`/assets/${assetId}/checkin`, null, {
      params: { damaged: checkin.value.damaged === "true" }
    });
    message.value = "退库成功";
  } catch (err) {
    message.value = "退库失败，请检查资产状态。";
  }
};

const submitTransfer = async () => {
  message.value = "";
  try {
    const assetId = await resolveAssetId(transfer.value.asset);
    if (!assetId) {
      message.value = "找不到资产，请确认输入。";
      return;
    }
    await api.post(`/assets/${assetId}/transfer`, null, {
      params: { dept: transfer.value.dept }
    });
    message.value = "调拨成功";
  } catch (err) {
    message.value = "调拨失败，请检查参数。";
  }
};
</script>

<style scoped></style>
