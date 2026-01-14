<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">字段分类</h2>
          <p class="text-sm text-muted-foreground">管理系统资产字段的分类。</p>
        </div>
        <RouterLink to="/system-field-categories/new">
          <Button variant="outline">新增分类</Button>
        </RouterLink>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">分类名称</th>
            <th class="px-4 py-2">分类编码</th>
            <th class="px-4 py-2">排序</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in categories" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.code }}</td>
            <td class="px-4 py-2">{{ item.sort_order }}</td>
            <td class="px-4 py-2">{{ item.is_active ? "启用" : "停用" }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/system-field-categories/${item.id}/fields`">
                  <Button size="sm" variant="outline">字段</Button>
                </RouterLink>
                <RouterLink :to="`/system-field-categories/${item.id}/edit`">
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

const load = async () => {
  const { data } = await api.get("/system-field-categories");
  categories.value = data;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/system-field-categories/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

onMounted(load);
</script>
