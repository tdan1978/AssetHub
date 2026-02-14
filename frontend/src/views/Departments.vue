<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4 flex items-center justify-between">
      <div class="text-sm text-muted-foreground">部门支持多级树结构管理。</div>
      <RouterLink to="/departments/new">
        <Button>新增部门</Button>
      </RouterLink>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">部门名称</th>
            <th class="px-4 py-2">编码</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">排序</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in flatDepartments" :key="item.id" class="border-b">
            <td class="px-4 py-2">
              <div class="flex items-center gap-2" :style="{ paddingLeft: `${item.depth * 16}px` }">
                <span v-if="item.depth" class="text-muted-foreground">└</span>
                <span>{{ item.name }}</span>
              </div>
            </td>
            <td class="px-4 py-2">{{ item.code || "-" }}</td>
            <td class="px-4 py-2">{{ item.is_active ? "启用" : "停用" }}</td>
            <td class="px-4 py-2">{{ item.sort_order }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/departments/new?parent_id=${item.id}`">
                  <Button size="sm">新增下级</Button>
                </RouterLink>
                <RouterLink :to="`/people/new?dept_id=${item.id}`">
                  <Button size="sm">添加人员</Button>
                </RouterLink>
                <RouterLink :to="`/departments/${item.id}/edit`">
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
import { computed, onMounted, ref } from "vue";
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

const departments = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);

const flattenTree = (nodes, depth = 0) => {
  const result = [];
  for (const node of nodes || []) {
    result.push({ ...node, depth });
    if (node.children && node.children.length) {
      result.push(...flattenTree(node.children, depth + 1));
    }
  }
  return result;
};

const flatDepartments = computed(() => flattenTree(departments.value));

const loadDepartments = async () => {
  const { data } = await api.get("/departments/tree");
  departments.value = Array.isArray(data) ? data : [];
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/departments/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await loadDepartments();
};

onMounted(loadDepartments);
</script>



