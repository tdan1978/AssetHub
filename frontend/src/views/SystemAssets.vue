<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="grid gap-4 md:grid-cols-4 items-end">
        <div class="form-field">
          <label class="form-label">关键词</label>
          <Input v-model="q" placeholder="搜索系统名称/编码" />
        </div>
        <div class="form-field">
          <label class="form-label">系统状态</label>
          <Select v-model="status">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="系统状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="开发中">开发中</SelectItem>
              <SelectItem value="测试中">测试中</SelectItem>
              <SelectItem value="运行中">运行中</SelectItem>
              <SelectItem value="维护中">维护中</SelectItem>
              <SelectItem value="已下线">已下线</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex items-end gap-3 md:col-span-2">
          <Button :disabled="loading" @click="load">查询</Button>
          <RouterLink to="/systems/new">
            <Button variant="outline">新增系统</Button>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <div v-if="loading" class="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground">
        <Spinner class="size-5" />
        <span>加载中...</span>
      </div>
      <table v-else class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">系统名称</th>
            <th class="px-4 py-2">系统编码</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">分类</th>
            <th class="px-4 py-2">技术负责人</th>
            <th class="px-4 py-2">运维负责人</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            class="border-b cursor-pointer hover:bg-muted/40"
            @click="openDetail(item.id)"
          >
            <td class="px-4 py-2">{{ item.app_name }}</td>
            <td class="px-4 py-2">{{ item.app_code }}</td>
            <td class="px-4 py-2">{{ item.app_status }}</td>
            <td class="px-4 py-2">{{ item.app_category }}</td>
            <td class="px-4 py-2">{{ item.tech_owner }}</td>
            <td class="px-4 py-2">{{ item.ops_owner }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2" @click.stop>
                <RouterLink :to="`/systems/${item.id}/edit`" @click.stop>
                  <Button size="sm" variant="outline" @click.stop>编辑</Button>
                </RouterLink>
                <Button size="sm" variant="outline" @click.stop="askDelete(item.id)">删除</Button>
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

    <Drawer v-model:open="detailOpen">
      <DrawerContent class="w-full overflow-auto">
        <DrawerHeader>
          <DrawerTitle>系统资产详情</DrawerTitle>
          <DrawerDescription>查看系统基础信息与自定义字段。</DrawerDescription>
        </DrawerHeader>
        <div class="space-y-6 px-6 pb-8">
          <div v-for="category in visibleCategories" :key="category.id" class="space-y-3">
            <div class="text-sm font-semibold">{{ category.name }}</div>
            <div class="rounded-lg border bg-background">
              <div class="grid gap-2 p-4 md:grid-cols-3">
                <div v-for="field in category.fields" :key="field.id" class="flex items-start gap-3">
                  <div class="w-24 text-sm font-medium">{{ field.name }}</div>
                  <div class="text-sm text-muted-foreground">
                    {{ formatFieldValue(resolveFieldValue(field)) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from "../components/ui/drawer";
import { Spinner } from "../components/ui/spinner";
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
const loading = ref(false);
const confirmOpen = ref(false);
const pendingId = ref(null);
const detailOpen = ref(false);
const detail = ref(null);
const detailCategories = ref([]);
const detailValues = ref({});

const baseFieldKeys = new Set([
  "app_name",
  "app_code",
  "app_status",
  "access_url",
  "app_category",
  "arch_type",
  "dev_lang",
  "db_type",
  "deploy_type",
  "repo_url",
  "biz_owner",
  "tech_owner",
  "ops_owner",
  "sec_level"
]);

const load = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/systems", {
      params: {
        page: 1,
        size: 20,
        q: q.value || null,
        app_status: status.value === "all" ? null : status.value
      }
    });
    items.value = data.items;
  } finally {
    loading.value = false;
  }
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/systems/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

const formatFieldValue = (value) => {
  if (Array.isArray(value)) return value.join("，");
  if (value === null || value === undefined || value === "") return "-";
  return value;
};

const resolveFieldValue = (field) => {
  if (baseFieldKeys.has(field.field_key)) {
    return detail.value?.[field.field_key];
  }
  return detailValues.value[field.id];
};

const openDetail = async (id) => {
  detailOpen.value = true;
  detail.value = null;
  detailCategories.value = [];
  detailValues.value = {};
  const [detailRes, categoriesRes, valuesRes] = await Promise.all([
    api.get(`/systems/${id}`),
    api.get("/system-field-categories/tree"),
    api.get(`/systems/${id}/fields`)
  ]);
  detail.value = detailRes.data;
  detailCategories.value = categoriesRes.data;
  const map = {};
  for (const item of valuesRes.data) {
    map[item.field_id] = item.value;
  }
  detailValues.value = map;
};

const visibleCategories = computed(() =>
  detailCategories.value.filter((category) => Array.isArray(category.fields) && category.fields.length > 0)
);

onMounted(load);
</script>
