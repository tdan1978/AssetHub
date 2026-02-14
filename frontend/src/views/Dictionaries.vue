<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-semibold">数据源管理</h2>
        <p class="mt-1 text-sm text-muted-foreground">维护静态字典类型与字典项。</p>
      </div>
      <Button v-if="canManage" @click="goCreate">新建字典类型</Button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">名称</th>
            <th class="px-4 py-2">编码</th>
            <th class="px-4 py-2">范围</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in types" :key="item.id" class="border-b">
            <td class="px-4 py-2">
              <div class="font-medium">{{ item.name }}</div>
            </td>
            <td class="px-4 py-2 text-sm text-muted-foreground">{{ item.code }}</td>
            <td class="px-4 py-2">{{ scopeLabel(item.scope) }}</td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-2">
                <Switch
                  :modelValue="item.is_active"
                  :disabled="!canManage"
                  @update:modelValue="(val) => toggleActive(item, val)"
                />
                <span class="text-sm" :class="item.is_active ? 'text-foreground' : 'text-muted-foreground'">
                  {{ item.is_active ? "启用" : "停用" }}
                </span>
              </div>
            </td>
            <td class="px-4 py-2 text-right">
              <div class="flex items-center justify-end gap-2">
                <Button variant="outline" size="sm" @click="goEdit(item.id)">编辑</Button>
                <AlertDialog v-if="canManage">
                  <AlertDialogTrigger as-child>
                    <Button variant="destructive" size="sm">删除</Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>确认删除</AlertDialogTitle>
                      <AlertDialogDescription>删除后将无法恢复。</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>取消</AlertDialogCancel>
                      <AlertDialogAction @click="confirmDelete(item)">删除</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </td>
          </tr>
          <tr v-if="types.length === 0">
            <td class="px-4 py-6 text-center text-sm text-muted-foreground" colspan="5">暂无字典类型</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Switch } from "../components/ui/switch";
import { toast } from "../components/ui/sonner";
import { useAuthStore } from "../stores/auth";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../components/ui/alert-dialog";

const router = useRouter();
const auth = useAuthStore();
const types = ref([]);

const canManage = computed(() => {
  if (auth.roleCode === "super_admin") return true;
  return (auth.permissions || []).includes("dictionaries:update");
});

const loadTypes = async () => {
  const { data } = await api.get("/dictionaries/types");
  types.value = Array.isArray(data) ? data : [];
};

const scopeLabel = (scope) => {
  if (scope === "office") return "办公硬件";
  if (scope === "datacenter") return "数据中心硬件";
  if (scope === "software") return "软件资产";
  if (scope === "system") return "系统资产";
  return "通用";
};

const toggleActive = async (item, value) => {
  const original = item.is_active;
  item.is_active = Boolean(value);
  try {
    await api.put(`/dictionaries/types/${item.id}`, {
      ...item,
      is_active: item.is_active,
    });
    toast.success(item.is_active ? "已启用" : "已停用");
  } catch (error) {
    item.is_active = original;
    toast.error(error?.response?.data?.detail || "状态更新失败");
  }
};

const confirmDelete = async (item) => {
  try {
    await api.delete(`/dictionaries/types/${item.id}`);
    toast.success("已删除");
    await loadTypes();
  } catch (error) {
    toast.error(error?.response?.data?.detail || "删除失败");
  }
};

const goEdit = (id) => {
  router.push(`/dictionaries/${id}/edit`);
};

const goCreate = () => {
  router.push("/dictionaries/new");
};

onMounted(async () => {
  await loadTypes();
});
</script>

<style scoped></style>



