<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="grid gap-4 md:grid-cols-4 items-end">
        <div class="form-field">
          <label class="form-label">关键词</label>
          <Input v-model="q" placeholder="搜索软件名称/厂商" />
        </div>
        <div class="flex items-end gap-3 md:col-span-3">
          <Button :disabled="loading" @click="load">查询</Button>
          <RouterLink to="/licenses/new">
            <Button variant="outline">新增软件</Button>
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
            <th class="px-4 py-2">软件名称</th>
            <th class="px-4 py-2">厂商</th>
            <th class="px-4 py-2">授权类型</th>
            <th class="px-4 py-2">总席位</th>
            <th class="px-4 py-2">已用</th>
            <th class="px-4 py-2">到期</th>
            <th class="px-4 py-2">合规状态</th>
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
            <td class="px-4 py-2">{{ item.software_name }}</td>
            <td class="px-4 py-2">{{ item.vendor }}</td>
            <td class="px-4 py-2">{{ item.license_type }}</td>
            <td class="px-4 py-2">{{ item.total_quantity }}</td>
            <td class="px-4 py-2">{{ item.used_quantity }}</td>
            <td class="px-4 py-2">{{ item.expire_at }}</td>
            <td class="px-4 py-2">{{ item.compliance_status }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2" @click.stop>
                <RouterLink :to="`/licenses/${item.id}/edit`" @click.stop>
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
          <DrawerTitle>软件资产详情</DrawerTitle>
          <DrawerDescription>查看软件基础信息与自定义字段。</DrawerDescription>
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
const loading = ref(false);
const confirmOpen = ref(false);
const pendingId = ref(null);
const detailOpen = ref(false);
const detail = ref(null);
const detailCategories = ref([]);
const detailValues = ref({});

const baseFieldKeys = new Set([
  "software_name",
  "version",
  "vendor",
  "category",
  "vendor_url",
  "license_type",
  "billing_mode",
  "license_key",
  "total_quantity",
  "used_quantity",
  "activation_limit",
  "expiry_type",
  "expire_at",
  "renewal_at",
  "compliance_status",
  "cost",
  "purchase_date",
  "order_no",
  "supplier"
]);

const load = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/licenses", { params: { page: 1, size: 20, q: q.value || null } });
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
  await api.delete(`/licenses/${pendingId.value}`);
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
    api.get(`/licenses/${id}`),
    api.get("/software-field-categories/tree"),
    api.get(`/licenses/${id}/fields`)
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

<style scoped></style>
