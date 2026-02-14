<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-semibold">角色权限</h2>
        <p class="mt-1 text-sm text-muted-foreground">管理系统中的角色与权限入口。</p>
      </div>
      <Button v-if="canManageRoles" @click="goCreate">新建角色</Button>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">角色名称</th>
            <th class="px-4 py-2">编码</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in roles" :key="role.id" class="border-b">
            <td class="px-4 py-2">
              <div class="font-medium">{{ role.name }}</div>
            </td>
            <td class="px-4 py-2 text-sm text-muted-foreground">{{ role.code }}</td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-2">
                <Switch
                  :modelValue="role.is_active"
                  :disabled="!canManageRoles || isProtected(role.code)"
                  @update:modelValue="(val) => toggleActive(role, val)"
                />
                <span class="text-sm" :class="role.is_active ? 'text-foreground' : 'text-muted-foreground'">
                  {{ role.is_active ? "启用" : "禁用" }}
                </span>
              </div>
            </td>
            <td class="px-4 py-2 text-right">
              <div class="flex items-center justify-end gap-2">
                <Button variant="outline" size="sm" @click="goEdit(role.id)">编辑</Button>
                <AlertDialog v-if="canManageRoles">
                  <AlertDialogTrigger as-child>
                    <Button
                      variant="destructive"
                      size="sm"
                      :disabled="isProtected(role.code)"
                    >
                      删除
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>确认删除</AlertDialogTitle>
                      <AlertDialogDescription>
                        删除后不可恢复，请确认没有用户使用该角色。
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>取消</AlertDialogCancel>
                      <AlertDialogAction @click="confirmDelete(role)">确认删除</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </td>
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
const roles = ref([]);

const protectedRoleCodes = new Set([
  "super_admin",
]);

const canManageRoles = computed(() => {
  if (auth.roleCode === "super_admin") return true;
  return (auth.permissions || []).includes("roles:update");
});

const isProtected = (code) => protectedRoleCodes.has(code);

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data || [];
};

const toggleActive = async (role, value) => {
  const next = Boolean(value);
  const original = role.is_active;
  role.is_active = next;
  try {
    await api.patch(`/roles/${role.id}`, { is_active: next });
    toast.success(next ? "角色已启用" : "角色已禁用");
  } catch (error) {
    role.is_active = original;
    toast.error(error?.response?.data?.detail || "状态更新失败");
  }
};

const confirmDelete = async (role) => {
  try {
    await api.delete(`/roles/${role.id}`);
    toast.success("角色已删除");
    await loadRoles();
  } catch (error) {
    toast.error(error?.response?.data?.detail || "删除失败");
  }
};

const goEdit = (id) => {
  router.push(`/roles/${id}/edit`);
};

const goCreate = () => {
  router.push("/roles/new");
};

onMounted(async () => {
  await loadRoles();
});
</script>

<style scoped></style>



