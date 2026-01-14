<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">字段列表</h2>
          <p class="text-sm text-muted-foreground">维护分类下的字段定义。</p>
        </div>
        <div class="flex gap-2">
          <RouterLink to="/software-field-categories">
            <Button variant="outline">返回分类</Button>
          </RouterLink>
          <RouterLink :to="`/software-field-categories/${categoryId}/fields/new`">
            <Button variant="outline">新增字段</Button>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">字段名称</th>
            <th class="px-4 py-2">字段代码</th>
            <th class="px-4 py-2">类型</th>
            <th class="px-4 py-2">必填</th>
            <th class="px-4 py-2">排序</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in fields" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.field_key }}</td>
            <td class="px-4 py-2">{{ typeLabels[item.field_type] || item.field_type }}</td>
            <td class="px-4 py-2">{{ item.is_required ? "是" : "否" }}</td>
            <td class="px-4 py-2">{{ item.sort_order }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/software-field-categories/${categoryId}/fields/${item.id}/edit`">
                  <Button size="sm" variant="outline">编辑</Button>
                </RouterLink>
                <Button size="sm" variant="outline" @click="askDelete(item.id)">删除</Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AlertDialog v-if="confirmOpen" v-model:open="confirmOpen">
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
const fields = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);
const categoryId = ref(0);

const typeLabels = {
  text: "文本",
  textarea: "多行文本",
  number: "数字",
  date: "日期",
  single_select: "单选",
  multi_select: "多选",
  boolean: "布尔"
};

const load = async () => {
  const { data } = await api.get(`/software-field-categories/${categoryId.value}/fields`);
  fields.value = data;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/software-field-categories/fields/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

const init = () => {
  categoryId.value = Number(route.params.id);
  if (Number.isNaN(categoryId.value)) {
    categoryId.value = 0;
  }
  if (categoryId.value) {
    load();
  }
};

onMounted(init);
</script>
