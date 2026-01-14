<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">系统消息</h2>
          <p class="text-sm text-muted-foreground">查看全部提醒信息。</p>
        </div>
        <Button variant="outline" @click="markAllRead" :disabled="!items.length">全部已读</Button>
      </div>
    </div>

    <div class="card">
      <div v-if="loading" class="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground">
        <Spinner class="size-5" />
        <span>加载中...</span>
      </div>
      <div v-else-if="!items.length" class="py-10 text-center text-sm text-muted-foreground">暂无消息</div>
      <table v-else class="table">
        <thead>
          <tr>
            <th>标题</th>
            <th>内容</th>
            <th>到期日</th>
            <th>提醒日</th>
            <th>类型</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td>{{ item.title }}</td>
            <td class="max-w-[320px] truncate">{{ item.message }}</td>
            <td>{{ item.due_date || "-" }}</td>
            <td>{{ item.remind_at || "-" }}</td>
            <td>{{ typeLabels[item.entity_type] || item.entity_type }}</td>
            <td>
              <span v-if="isRead(item.id)" class="text-xs text-muted-foreground">已读</span>
              <span v-else class="text-xs font-medium text-primary">未读</span>
            </td>
            <td>
              <Button size="sm" variant="outline" class="min-w-[84px]" @click="toggleRead(item.id)">
                {{ isRead(item.id) ? "设为未读" : "已读" }}
              </Button>
            </td>
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
import { Spinner } from "../components/ui/spinner";

const items = ref([]);
const loading = ref(false);
const readIds = ref(new Set());

const typeLabels = {
  asset: "资产",
  system: "系统",
  license: "软件"
};

const load = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/notifications");
    items.value = data;
  } finally {
    loading.value = false;
  }
};

const loadReadIds = () => {
  const cached = localStorage.getItem("assethub_read_notifications");
  if (!cached) return;
  try {
    readIds.value = new Set(JSON.parse(cached));
  } catch {
    readIds.value = new Set();
  }
};

const persistReadIds = (nextSet) => {
  readIds.value = new Set(nextSet);
  localStorage.setItem("assethub_read_notifications", JSON.stringify([...readIds.value]));
  window.dispatchEvent(new Event("assethub-notifications-updated"));
};

const markRead = (id) => {
  const next = new Set(readIds.value);
  next.add(id);
  persistReadIds(next);
};

const markUnread = (id) => {
  const next = new Set(readIds.value);
  next.delete(id);
  persistReadIds(next);
};

const markAllRead = () => {
  const next = new Set(readIds.value);
  for (const item of items.value) {
    next.add(item.id);
  }
  persistReadIds(next);
};

const toggleRead = (id) => {
  if (isRead(id)) {
    markUnread(id);
  } else {
    markRead(id);
  }
};

const isRead = (id) => readIds.value.has(id);

onMounted(() => {
  loadReadIds();
  load();
});
</script>
