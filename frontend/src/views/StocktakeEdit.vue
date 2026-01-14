<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑盘点</h2>
          <p class="text-sm text-muted-foreground">更新盘点任务信息。</p>
        </div>
        <RouterLink to="/stocktakes">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">盘点名称</label>
          <Input v-model="form.name" placeholder="盘点名称" />
        </div>
        <div class="form-field">
          <label class="form-label">范围描述</label>
          <Input v-model="form.scope" placeholder="范围描述" />
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

const route = useRoute();
const router = useRouter();
const taskId = Number(route.params.id);
const form = ref({ name: "", scope: "" });

const load = async () => {
  const { data } = await api.get(`/stocktakes/${taskId}`);
  form.value = { name: data.name, scope: data.scope || "" };
};

const save = async () => {
  await api.put(`/stocktakes/${taskId}`, form.value);
  router.push("/stocktakes");
};

onMounted(load);
</script>
