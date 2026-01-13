<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <RouterLink to="/users/new">
        <Button variant="outline">新增用户</Button>
      </RouterLink>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">ID</th>
            <th class="px-4 py-2">用户名</th>
            <th class="px-4 py-2">姓名</th>
            <th class="px-4 py-2">角色</th>
            <th class="px-4 py-2">部门</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.id }}</td>
            <td class="px-4 py-2">{{ item.username }}</td>
            <td class="px-4 py-2">{{ item.full_name }}</td>
            <td class="px-4 py-2">{{ roleMap[item.role_id] || item.role_id }}</td>
            <td class="px-4 py-2">{{ item.dept }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/users/${item.id}/edit`">
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
const roles = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);
const roleMap = computed(() => {
  const map = {};
  for (const role of roles.value) {
    map[role.id] = role.name;
  }
  return map;
});

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data;
};

const loadUsers = async () => {
  const { data } = await api.get("/users", { params: { page: 1, size: 50 } });
  items.value = data.items;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/users/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await loadUsers();
};

onMounted(async () => {
  await loadRoles();
  await loadUsers();
});
</script>

<style scoped></style>
