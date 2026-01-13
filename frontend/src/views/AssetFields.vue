<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">字段配置</h2>
          <p class="text-sm text-muted-foreground">类型：{{ category?.name || "" }}</p>
        </div>
        <div class="flex gap-2">
          <RouterLink to="/asset-types">
            <Button variant="outline">返回类型</Button>
          </RouterLink>
          <RouterLink :to="`/asset-types/${categoryId}/fields/new`">
            <Button variant="outline">新增字段</Button>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th>名称</th>
            <th>键</th>
            <th>类型</th>
            <th>必填</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in fields" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.field_key }}</td>
            <td>{{ item.field_type }}</td>
            <td>{{ item.is_required ? "是" : "否" }}</td>
            <td>
              <div class="flex gap-2">
                <RouterLink :to="`/asset-types/${categoryId}/fields/${item.id}/edit`">
                  <Button size="sm" variant="outline">编辑</Button>
                </RouterLink>
                <Button size="sm" variant="outline" @click="askDelete(item.id)">删除</Button>
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
import { useRoute } from "vue-router";
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

const route = useRoute();
const categoryId = Number(route.params.id);
const fields = ref([]);
const category = ref(null);
const confirmOpen = ref(false);
const pendingId = ref(null);

const load = async () => {
  const { data } = await api.get("/categories");
  category.value = data.find((c) => c.id === categoryId) || null;
  const res = await api.get(`/categories/${categoryId}/fields`);
  fields.value = res.data;
};

const askDelete = (fieldId) => {
  pendingId.value = fieldId;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/categories/fields/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

onMounted(load);
</script>
