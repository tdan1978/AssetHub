<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="flex flex-wrap items-center gap-3">
        <input v-model="q" class="input" placeholder="搜索 SN/名称/编号" />
        <select v-model="status" class="input">
          <option :value="null">全部</option>
          <option :value="0">闲置</option>
          <option :value="1">在用</option>
          <option :value="2">维修</option>
          <option :value="3">待报废</option>
          <option :value="4">已报废</option>
        </select>
        <Button @click="load">查询</Button>
        <Button variant="outline" @click="showCreate = !showCreate">
          {{ showCreate ? "收起新增" : "新增资产" }}
        </Button>
      </div>
    </div>

    <div v-if="showCreate" class="rounded-lg border bg-background p-4">
      <h2 class="mb-4 text-base font-semibold">新增资产</h2>
      <div class="grid gap-3 md:grid-cols-4">
        <input v-model="form.sn" class="input" placeholder="SN" />
        <input v-model="form.asset_no" class="input" placeholder="编号" />
        <input v-model="form.name" class="input" placeholder="名称" />
        <input v-model="form.category" class="input" placeholder="分类" />
      </div>
      <div class="mt-4">
        <Button @click="create">保存</Button>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="w-full text-sm">
        <thead class="border-b bg-muted/40 text-left">
          <tr>
            <th class="px-4 py-2">编号</th>
            <th class="px-4 py-2">SN</th>
            <th class="px-4 py-2">名称</th>
            <th class="px-4 py-2">分类</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">部门</th>
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
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";

const items = ref([]);
const q = ref("");
const status = ref(null);
const showCreate = ref(false);
const form = ref({
  sn: "",
  asset_no: "",
  name: "",
  category: "",
  status: 0
});

const load = async () => {
  const { data } = await api.get("/assets", {
    params: { page: 1, size: 20, q: q.value || null, status: status.value }
  });
  items.value = data.items;
};

const create = async () => {
  await api.post("/assets", form.value);
  form.value = { sn: "", asset_no: "", name: "", category: "", status: 0 };
  showCreate.value = false;
  await load();
};

onMounted(load);
</script>

<style scoped></style>
