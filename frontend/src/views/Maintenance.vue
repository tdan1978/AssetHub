<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">维保与报修</h2>
          <p class="mt-1 text-sm text-muted-foreground">记录供应商、维保合同与维修费用。</p>
        </div>
        <div class="flex gap-2">
          <RouterLink to="/maintenance/repairs/new">
            <Button variant="outline">新增报修</Button>
          </RouterLink>
          <RouterLink to="/maintenance/info">
            <Button variant="outline">维保信息</Button>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-sm font-semibold">维修记录</h3>
      <table class="table mt-3">
        <thead>
          <tr>
            <th>资产</th>
            <th>故障</th>
            <th>费用</th>
            <th>状态</th>
            <th>时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in repairs" :key="item.id">
            <td>{{ item.asset_id }}</td>
            <td>{{ item.issue }}</td>
            <td>{{ item.cost || "-" }}</td>
            <td>{{ item.status }}</td>
            <td>{{ item.created_at || "-" }}</td>
            <td>
              <div class="flex gap-2">
                <RouterLink :to="`/maintenance/repairs/${item.id}/edit`">
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

const repairs = ref([]);
const confirmOpen = ref(false);
const pendingId = ref(null);

const loadRepairs = async () => {
  const { data } = await api.get("/maintenance/repairs");
  repairs.value = data;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/maintenance/repairs/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await loadRepairs();
};

onMounted(loadRepairs);
</script>
