<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <Button @click="showCreate = !showCreate">
        {{ showCreate ? "收起新增" : "新增授权" }}
      </Button>
    </div>

    <div v-if="showCreate" class="rounded-lg border bg-background p-4">
      <h2 class="mb-4 text-base font-semibold">新增授权</h2>
      <div class="grid gap-3 md:grid-cols-2">
        <input v-model="form.name" class="input" placeholder="软件名称" />
        <input v-model="form.total_qty" class="input" type="number" min="1" placeholder="总数" />
        <textarea v-model="form.license_key" class="input min-h-[80px] md:col-span-2" placeholder="授权密钥"></textarea>
      </div>
      <div class="mt-4">
        <Button @click="create">保存</Button>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="w-full text-sm">
        <thead class="border-b bg-muted/40 text-left">
          <tr>
            <th class="px-4 py-2">软件</th>
            <th class="px-4 py-2">总数</th>
            <th class="px-4 py-2">已分配</th>
            <th class="px-4 py-2">到期</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.total_qty }}</td>
            <td class="px-4 py-2">{{ item.used_qty }}</td>
            <td class="px-4 py-2">{{ item.expire_at }}</td>
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
const showCreate = ref(false);
const form = ref({ name: "", license_key: "", total_qty: 1, used_qty: 0 });

const load = async () => {
  const { data } = await api.get("/licenses", { params: { page: 1, size: 20 } });
  items.value = data.items;
};

const create = async () => {
  await api.post("/licenses", form.value);
  form.value = { name: "", license_key: "", total_qty: 1, used_qty: 0 };
  showCreate.value = false;
  await load();
};

onMounted(load);
</script>

<style scoped></style>
