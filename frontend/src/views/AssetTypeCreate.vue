<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增资产类型</h2>
          <p class="text-sm text-muted-foreground">定义资产类型的基础信息。</p>
        </div>
        <RouterLink to="/asset-types">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid">
        <div class="form-field">
          <label class="form-label">类型名称</label>
          <Input v-model="form.name" placeholder="类型名称" />
        </div>
        <div class="form-field">
          <label class="form-label">类型编码</label>
          <Input v-model="form.code" placeholder="类型编码" />
        </div>
        <div class="form-field">
          <label class="form-label">描述</label>
          <Input v-model="form.description" placeholder="描述" />
        </div>
      </div>
      <div class="mt-4">
        <Button @click="save">保存</Button>
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
const form = ref({ name: "", code: "", description: "", is_active: true });

const save = async () => {
  if (!form.value.name) return;
  await api.post("/categories", form.value);
  router.push("/asset-types");
};
</script>
