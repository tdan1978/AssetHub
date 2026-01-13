<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑资产类型</h2>
          <p class="text-sm text-muted-foreground">更新类型基础信息。</p>
        </div>
        <RouterLink to="/asset-types">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="grid gap-3 md:grid-cols-3">
        <Input v-model="form.name" placeholder="类型名称" />
        <Input v-model="form.code" placeholder="类型编码" />
        <Input v-model="form.description" placeholder="描述" />
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
const categoryId = Number(route.params.id);
const form = ref({ name: "", code: "", description: "", is_active: true });

const load = async () => {
  const { data } = await api.get("/categories");
  const item = data.find((c) => c.id === categoryId);
  if (item) {
    form.value = { ...item };
  }
};

const save = async () => {
  await api.put(`/categories/${categoryId}`, form.value);
  router.push("/asset-types");
};

onMounted(load);
</script>
