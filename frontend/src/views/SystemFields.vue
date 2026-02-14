<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">字段列表</h2>
          <p class="text-sm text-muted-foreground">维护分类下的字段定义。</p>
          <p class="text-xs text-muted-foreground">拖拽行可调整字段顺序</p>
        </div>
        <div class="flex gap-2">
          <RouterLink to="/system-field-categories">
            <Button variant="outline">返回分类</Button>
          </RouterLink>
          <RouterLink :to="`/system-field-categories/${categoryId}/fields/new`">
            <Button>新增字段</Button>
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
          <tr
            v-for="item in fields"
            :key="item.id"
            class="border-b cursor-move"
            :class="{ 'opacity-60': draggedFieldId === item.id }"
            :draggable="!savingOrder"
            @dragstart="onDragStart(item.id)"
            @dragover.prevent
            @drop="onDrop(item.id)"
            @dragend="onDragEnd"
          >
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.field_key }}</td>
            <td class="px-4 py-2">{{ typeLabels[item.field_type] || item.field_type }}</td>
            <td class="px-4 py-2">{{ item.is_required ? "是" : "否" }}</td>
            <td class="px-4 py-2">{{ item.sort_order }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/system-field-categories/${categoryId}/fields/${item.id}/edit`">
                  <Button size="sm" variant="outline">编辑</Button>
                </RouterLink>
                <Button size="sm" variant="destructive" :disabled="item.in_use || item.is_builtin" @click="askDelete(item.id)">
                  {{ item.is_builtin ? "系统字段" : item.in_use ? "已使用" : "删除" }}
                </Button>
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
import { toast } from "../components/ui/sonner";
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
const draggedFieldId = ref(null);
const savingOrder = ref(false);
const typeLabels = {
  text: "文本",
  textarea: "多行文本",
  markdown: "Markdown 文档",
  topology: "拓扑图",
  number: "数字",
  date: "日期",
  single_select: "单选",
  combo_select: "单选",
  multi_select: "多选",
  compound: "组合字段",
  boolean: "布尔"
};

const load = async () => {
  const { data } = await api.get(`/system-field-categories/${categoryId.value}/fields`);
  fields.value = (Array.isArray(data) ? data : []).sort((a, b) => {
    const left = Number(a?.sort_order || 0);
    const right = Number(b?.sort_order || 0);
    if (left !== right) return left - right;
    return Number(a?.id || 0) - Number(b?.id || 0);
  });
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/system-field-categories/fields/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

const onDragStart = (fieldId) => {
  draggedFieldId.value = fieldId;
};

const onDragEnd = () => {
  draggedFieldId.value = null;
};

const persistOrder = async () => {
  savingOrder.value = true;
  const snapshot = fields.value.map((item) => ({ ...item }));
  try {
    const changed = [];
    fields.value.forEach((item, index) => {
      const nextSort = index + 1;
      if (Number(item.sort_order || 0) !== nextSort) {
        item.sort_order = nextSort;
        changed.push({ id: item.id, sort_order: nextSort });
      }
    });
    for (const item of changed) {
      await api.put(`/system-field-categories/fields/${item.id}`, { sort_order: item.sort_order });
    }
    if (changed.length) {
      toast.success("字段顺序已更新");
    }
  } catch (error) {
    fields.value = snapshot;
    toast.error(error?.response?.data?.detail || "更新字段顺序失败");
  } finally {
    savingOrder.value = false;
  }
};

const onDrop = async (targetFieldId) => {
  if (savingOrder.value) return;
  const sourceId = draggedFieldId.value;
  if (!sourceId || sourceId === targetFieldId) return;
  const sourceIndex = fields.value.findIndex((item) => item.id === sourceId);
  const targetIndex = fields.value.findIndex((item) => item.id === targetFieldId);
  if (sourceIndex < 0 || targetIndex < 0) return;
  const [moved] = fields.value.splice(sourceIndex, 1);
  fields.value.splice(targetIndex, 0, moved);
  draggedFieldId.value = null;
  await persistOrder();
};

const categoryId = ref(0);

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



