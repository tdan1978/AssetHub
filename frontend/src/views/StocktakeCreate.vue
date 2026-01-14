<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">发起盘点</h2>
          <p class="text-sm text-muted-foreground">按部门/区域/分类发起盘点任务。</p>
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
        <Button @click="save">发起盘点</Button>
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
const form = ref({ name: "", scope: "" });

const save = async () => {
  if (!form.value.name) return;
  await api.post("/stocktakes", form.value);
  router.push("/stocktakes");
};
</script>
