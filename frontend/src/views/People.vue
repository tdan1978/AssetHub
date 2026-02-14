<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4 flex items-center justify-between">
      <div class="text-sm text-muted-foreground">人员信息独立管理，可作为资产字段数据源。</div>
      <RouterLink to="/people/new">
        <Button variant="outline">新增人员</Button>
      </RouterLink>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">姓名</th>
            <th class="px-4 py-2">工号</th>
            <th class="px-4 py-2">部门</th>
            <th class="px-4 py-2">手机号</th>
            <th class="px-4 py-2">邮箱</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.emp_code || "-" }}</td>
            <td class="px-4 py-2">{{ deptMap[item.dept_id] || "-" }}</td>
            <td class="px-4 py-2">{{ item.phone || "-" }}</td>
            <td class="px-4 py-2">{{ item.email || "-" }}</td>
            <td class="px-4 py-2">{{ item.status || "-" }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/people/${item.id}/edit`">
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

const items = ref([]);
const departments = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);

const deptMap = computed(() => {
  const map = {};
  for (const dept of departments.value) {
    map[dept.id] = dept.name;
  }
  return map;
});

const loadDepartments = async () => {
  const { data } = await api.get("/departments", { params: { page: 1, size: 500 } });
  departments.value = data.items || [];
};

const loadPeople = async () => {
  const { data } = await api.get("/people", { params: { page: 1, size: 100 } });
  items.value = data.items || [];
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/people/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await loadPeople();
};

onMounted(async () => {
  await loadDepartments();
  await loadPeople();
});
</script>



