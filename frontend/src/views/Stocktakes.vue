<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <Button @click="showCreate = !showCreate">
        {{ showCreate ? "收起发起" : "发起盘点" }}
      </Button>
    </div>

    <div v-if="showCreate" class="rounded-lg border bg-background p-4">
      <h2 class="mb-4 text-base font-semibold">发起盘点</h2>
      <div class="grid gap-3 md:grid-cols-3">
        <input v-model="name" class="input" placeholder="盘点名称" />
        <input v-model="scope" class="input" placeholder="范围描述" />
        <div class="flex items-center">
          <Button @click="create">发起盘点</Button>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="w-full text-sm">
        <thead class="border-b bg-muted/40 text-left">
          <tr>
            <th class="px-4 py-2">ID</th>
            <th class="px-4 py-2">名称</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">范围</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.id }}</td>
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.status }}</td>
            <td class="px-4 py-2">{{ item.scope }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";

const name = ref("");
const scope = ref("");
const items = ref([]);
const showCreate = ref(false);

const create = async () => {
  if (!name.value) return;
  const { data } = await api.post("/stocktakes", { name: name.value, scope: scope.value });
  items.value = [data, ...items.value];
  name.value = "";
  scope.value = "";
  showCreate.value = false;
};
</script>

<style scoped></style>
