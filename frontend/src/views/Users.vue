<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="flex flex-wrap items-center gap-2">
        <RouterLink to="/users/new">
          <Button>新增用户</Button>
        </RouterLink>
        <RouterLink to="/users/ldap">
          <Button variant="secondary">LDAP 设置</Button>
        </RouterLink>
        <Button variant="secondary" @click="syncLdap" :disabled="syncing">
          {{ syncing ? "同步中..." : "同步 LDAP" }}
        </Button>
        <span v-if="syncMessage" class="text-sm" :class="syncError ? 'text-destructive' : 'text-green-600'">
          {{ syncMessage }}
        </span>
      </div>
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
            <th class="px-4 py-2">电话</th>
            <th class="px-4 py-2">企业微信名</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.id }}</td>
            <td class="px-4 py-2">{{ item.username }}</td>
            <td class="px-4 py-2">{{ item.full_name }}</td>
            <td class="px-4 py-2">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="role in item.roles || []"
                  :key="role.id"
                  class="rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                >
                  {{ role.name }}
                </span>
              </div>
            </td>
            <td class="px-4 py-2">{{ item.dept }}</td>
            <td class="px-4 py-2">{{ item.phone || "-" }}</td>
            <td class="px-4 py-2">{{ item.wecom_name || "-" }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/users/${item.id}/edit`">
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

const items = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);
const syncing = ref(false);
const syncMessage = ref("");
const syncError = ref(false);

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

const syncLdap = async () => {
  syncing.value = true;
  syncMessage.value = "";
  syncError.value = false;
  try {
    const { data } = await api.post("/ldap/sync");
    syncMessage.value = data.ok
      ? `同步完成：新增 ${data.created}，更新 ${data.updated}，跳过 ${data.skipped}`
      : "同步失败";
    syncError.value = !data.ok;
    await loadUsers();
  } catch (err) {
    syncError.value = true;
    syncMessage.value = err?.response?.data?.detail || "同步失败";
  } finally {
    syncing.value = false;
  }
};

onMounted(async () => {
  await loadUsers();
});
</script>

<style scoped></style>



