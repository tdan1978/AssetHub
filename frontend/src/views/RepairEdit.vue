<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑报修</h2>
          <p class="text-sm text-muted-foreground">更新维修记录。</p>
        </div>
        <RouterLink to="/maintenance">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">资产 ID</label>
          <Input v-model="form.asset_id" placeholder="资产 ID" disabled />
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
          <Input v-model="form.cost" placeholder="费用" />
        </div>
        <div class="form-field">
          <label class="form-label">状态</label>
          <Select v-model="form.status">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="open">处理中</SelectItem>
              <SelectItem value="closed">已修复</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div class="mt-4">
        <Button @click="save">保存</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

const route = useRoute();
const router = useRouter();
const repairId = Number(route.params.id);
const form = ref({ asset_id: "", issue: "", vendor: "", cost: "", status: "open" });

const load = async () => {
  const { data } = await api.get(`/maintenance/repairs/${repairId}`);
  form.value = { ...data };
};

const save = async () => {
  await api.put(`/maintenance/repairs/${repairId}`, {
    issue: form.value.issue,
    vendor: form.value.vendor,
    cost: form.value.cost,
    status: form.value.status
  });
  router.push("/maintenance");
};

onMounted(load);
</script>
