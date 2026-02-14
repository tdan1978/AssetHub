<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">资产类型</h2>
          <p class="mt-1 text-sm text-muted-foreground">管理资产类型与字段配置。</p>
        </div>
        <RouterLink to="/asset-types/new">
          <Button variant="outline">新增类型</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>名称</th>
            <th>编码</th>
            <th>范围</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in categories" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.code || '-' }}</td>
            <td>{{ scopeLabels[item.usage_scope || "all"] }}</td>
            <td>{{ item.is_active ? '启用' : '停用' }}</td>
            <td>
              <div class="flex gap-2">
                <RouterLink :to="`/asset-types/${item.id}/fields`">
                  <Button size="sm" variant="default">字段</Button>
                </RouterLink>
                <RouterLink :to="`/asset-types/${item.id}/edit`">
                  <Button size="sm" variant="outline">编辑</Button>
                </RouterLink>
                <Button size="sm" variant="destructive" @click="askDelete(item.id)">删除</Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AlertDialog v-model:open="confirmOpen">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认删除</AlertDialogTitle>
          <AlertDialogDescription>删除后将无法恢复。</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>取消</AlertDialogCancel>
          <AlertDialogAction @click="confirmDelete">删除</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter
} from "../components/ui/alert-dialog";

const categories = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);
const scopeLabels = {
  all: "通用",
  office: "办公资产",
  datacenter: "数据中心资产"
};

const loadCategories = async () => {
  const { data } = await api.get("/categories");
  categories.value = data;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/categories/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await loadCategories();
};

onMounted(loadCategories);
</script>

<style scoped></style>



