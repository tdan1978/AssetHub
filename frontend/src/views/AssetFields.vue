<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">字段配置</h2>
          <p class="text-sm text-muted-foreground">类型：{{ category?.name || "" }}</p>
          <p class="text-xs text-muted-foreground">拖拽行可调整字段顺序</p>
        </div>
        <div class="flex gap-2">
          <RouterLink to="/asset-types">
            <Button variant="outline">返回类型</Button>
          </RouterLink>
          <RouterLink :to="`/asset-types/${categoryId}/fields/new`">
            <Button>新增字段</Button>
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
            <th>可重复</th>
            <th>排序</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in fields"
            :key="item.id"
            :draggable="!savingOrder"
            class="cursor-move"
            :class="{ 'opacity-60': draggedFieldId === item.id }"
            @dragstart="onDragStart(item.id)"
            @dragover.prevent
            @drop="onDrop(item.id)"
            @dragend="onDragEnd"
          >
            <td>{{ item.name }}</td>
            <td>{{ item.field_key }}</td>
            <td>{{ typeLabels[item.field_type] || item.field_type }}</td>
            <td>{{ item.is_required ? "是" : "否" }}</td>
            <td>{{ item.repeatable ? "是" : "否" }}</td>
            <td>{{ item.sort_order }}</td>
            <td>
              <div class="flex gap-2">
                <RouterLink :to="`/asset-types/${categoryId}/fields/${item.id}/edit`">
                  <Button size="sm" variant="outline">编辑</Button>
                </RouterLink>
                <Button size="sm" variant="destructive" :disabled="item.in_use" @click="askDelete(item.id)">
                  {{ item.in_use ? "已使用" : "删除" }}
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
const categoryId = Number(route.params.id);
const fields = ref([]);
const category = ref(null);
const confirmOpen = ref(false);
const pendingId = ref(null);
const draggedFieldId = ref(null);
const savingOrder = ref(false);
const typeLabels = {
  text: "文本",
  textarea: "多行文本",
  number: "数字",
  date: "日期",
  single_select: "单选",
  combo_select: "单选",
  multi_select: "多选",
  compound: "组合字段",
  boolean: "布尔"
};

const load = async () => {
  const { data } = await api.get("/categories");
  category.value = data.find((c) => c.id === categoryId) || null;
  const res = await api.get(`/categories/${categoryId}/fields`);
  fields.value = (Array.isArray(res.data) ? res.data : []).sort((a, b) => {
    const left = Number(a?.sort_order || 0);
    const right = Number(b?.sort_order || 0);
    if (left !== right) return left - right;
    return Number(a?.id || 0) - Number(b?.id || 0);
  });
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
      await api.put(`/categories/fields/${item.id}`, { sort_order: item.sort_order });
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

onMounted(load);
</script>



