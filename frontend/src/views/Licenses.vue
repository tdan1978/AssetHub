<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <RouterLink to="/licenses/new">
        <Button variant="outline">新增授权</Button>
      </RouterLink>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">软件</th>
            <th class="px-4 py-2">总数</th>
            <th class="px-4 py-2">已分配</th>
            <th class="px-4 py-2">到期</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.total_qty }}</td>
            <td class="px-4 py-2">{{ item.used_qty }}</td>
            <td class="px-4 py-2">{{ item.expire_at }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/licenses/${item.id}/edit`">
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

const items = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);

const load = async () => {
  const { data } = await api.get("/licenses", { params: { page: 1, size: 20 } });
  items.value = data.items;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/licenses/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

onMounted(load);
</script>

<style scoped></style>
