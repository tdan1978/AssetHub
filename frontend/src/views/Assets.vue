<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="flex flex-wrap items-center gap-3">
        <Input v-model="q" placeholder="搜索 SN/名称/编号" />
        <Select v-model="status">
          <SelectTrigger class="w-40">
            <SelectValue placeholder="状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部</SelectItem>
            <SelectItem value="0">闲置</SelectItem>
            <SelectItem value="1">在用</SelectItem>
            <SelectItem value="2">维修</SelectItem>
            <SelectItem value="3">待报废</SelectItem>
            <SelectItem value="4">已报废</SelectItem>
          </SelectContent>
        </Select>
        <Button @click="load">查询</Button>
        <RouterLink to="/assets/new">
          <Button variant="outline">新增资产</Button>
        </RouterLink>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">编号</th>
            <th class="px-4 py-2">SN</th>
            <th class="px-4 py-2">名称</th>
            <th class="px-4 py-2">分类</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">部门</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.asset_no }}</td>
            <td class="px-4 py-2">{{ item.sn }}</td>
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.category }}</td>
            <td class="px-4 py-2">{{ item.status }}</td>
            <td class="px-4 py-2">{{ item.dept }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2">
                <RouterLink :to="`/assets/${item.id}/edit`">
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
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
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
const q = ref("");
const status = ref("all");
const confirmOpen = ref(false);
const pendingId = ref(null);

const load = async () => {
  const { data } = await api.get("/assets", {
    params: {
      page: 1,
      size: 20,
      q: q.value || null,
      status: status.value === "all" ? null : Number(status.value)
    }
  });
  items.value = data.items;
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/assets/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

onMounted(load);
</script>

<style scoped></style>
