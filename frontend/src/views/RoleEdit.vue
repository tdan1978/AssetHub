<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-semibold">角色权限</h2>
        <p class="mt-1 text-sm text-muted-foreground">为指定角色分配资源与动作权限。</p>
      </div>
      <Button variant="outline" @click="goBack">返回列表</Button>
    </div>

    <div class="card">
      <div class="flex flex-wrap items-center justify-between gap-6">
        <div>
          <div class="text-xs text-muted-foreground">当前角色</div>
          <div class="text-lg font-semibold">{{ role?.name || "-" }}</div>
          <div class="text-xs text-muted-foreground">{{ role?.code || "" }}</div>
        </div>
        <div class="text-sm text-muted-foreground">超级管理员默认拥有全部权限，不可编辑。</div>
      </div>
    </div>

    <div class="card" v-if="role">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">资源</th>
            <th class="px-4 py-2">查看</th>
            <th class="px-4 py-2">新增</th>
            <th class="px-4 py-2">编辑</th>
            <th class="px-4 py-2">删除</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="res in resources" :key="res.key" class="border-b">
            <td class="px-4 py-2">{{ res.label }}</td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-3">
                <Switch
                  v-if="res.actions.includes('view')"
                  :modelValue="hasPermission(res.key, 'view')"
                  :disabled="isSuperAdmin"
                  @update:modelValue="(val) => togglePermission(res.key, 'view', val)"
                />
                <div v-if="showScope(res, 'view')" class="w-28">
                  <Select :modelValue="getScope(res.key, 'view')" @update:modelValue="(val) => setScope(res.key, 'view', val)">
                    <SelectTrigger>
                      <SelectValue placeholder="范围" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="own">本人</SelectItem>
                      <SelectItem value="all">全部</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </td>
            <td class="px-4 py-2">
              <Switch
                v-if="res.actions.includes('create')"
                :modelValue="hasPermission(res.key, 'create')"
                :disabled="isSuperAdmin"
                @update:modelValue="(val) => togglePermission(res.key, 'create', val)"
              />
            </td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-3">
                <Switch
                  v-if="res.actions.includes('update')"
                  :modelValue="hasPermission(res.key, 'update')"
                  :disabled="isSuperAdmin"
                  @update:modelValue="(val) => togglePermission(res.key, 'update', val)"
                />
                <div v-if="showScope(res, 'update')" class="w-28">
                  <Select :modelValue="getScope(res.key, 'update')" @update:modelValue="(val) => setScope(res.key, 'update', val)">
                    <SelectTrigger>
                      <SelectValue placeholder="范围" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="own">本人</SelectItem>
                      <SelectItem value="all">全部</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-3">
                <Switch
                  v-if="res.actions.includes('delete')"
                  :modelValue="hasPermission(res.key, 'delete')"
                  :disabled="isSuperAdmin"
                  @update:modelValue="(val) => togglePermission(res.key, 'delete', val)"
                />
                <div v-if="showScope(res, 'delete')" class="w-28">
                  <Select :modelValue="getScope(res.key, 'delete')" @update:modelValue="(val) => setScope(res.key, 'delete', val)">
                    <SelectTrigger>
                      <SelectValue placeholder="范围" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="own">本人</SelectItem>
                      <SelectItem value="all">全部</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="mt-4 flex flex-wrap items-center gap-3">
        <Button :disabled="isSuperAdmin || !canManageRoles" @click="save">保存权限</Button>
        <span class="text-sm text-muted-foreground">修改后立即生效</span>
      </div>
    </div>

    <div v-else class="card text-sm text-muted-foreground">未找到角色信息。</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Switch } from "../components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { toast } from "../components/ui/sonner";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const resources = ref([]);
const permissions = ref(new Map());
const role = ref(null);

const roleId = computed(() => Number(route.params.id));
const isSuperAdmin = computed(() => role.value?.code === "super_admin");
const canManageRoles = computed(() => {
  if (auth.roleCode === "super_admin") return true;
  return (auth.permissions || []).includes("roles:update");
});

const permissionKey = (resource, action) => `${resource}:${action}`;

const hasPermission = (resource, action) => permissions.value.has(permissionKey(resource, action));

const getScope = (resource, action) => {
  const key = permissionKey(resource, action);
  return permissions.value.get(key) || "all";
};

const setScope = (resource, action, scope) => {
  const key = permissionKey(resource, action);
  if (!permissions.value.has(key)) return;
  const next = new Map(permissions.value);
  next.set(key, scope || "all");
  permissions.value = next;
};

const showScope = (resource, action) => {
  if (!resource?.scopes || !resource.scopes.length) return false;
  if (!hasPermission(resource.key, action)) return false;
  return resource.key === "system_assets" && (action === "view" || action === "update" || action === "delete");
};

const togglePermission = (resource, action, enabled) => {
  const key = permissionKey(resource, action);
  const next = new Map(permissions.value);
  if (enabled) {
    if (!next.has(key)) {
      next.set(
        key,
        resource === "system_assets" && (action === "view" || action === "update" || action === "delete")
          ? "own"
          : "all"
      );
    }
  } else {
    next.delete(key);
  }
  permissions.value = next;
};

const loadRole = async () => {
  if (!roleId.value) return;
  const { data } = await api.get("/roles");
  role.value = (data || []).find((item) => item.id === roleId.value) || null;
};

const loadResources = async () => {
  const { data } = await api.get("/permissions/resources");
  resources.value = data || [];
};

const loadPermissions = async () => {
  if (!roleId.value) return;
  const { data } = await api.get(`/roles/${roleId.value}/permissions`);
  const next = new Map();
  data.forEach((item) => {
    next.set(permissionKey(item.resource, item.action), item.scope || "all");
  });
  permissions.value = next;
};

const save = async () => {
  if (!roleId.value) return;
  const payload = Array.from(permissions.value.entries()).map(([key, scope]) => {
    const [resource, action] = key.split(":");
    return { resource, action, scope };
  });
  try {
    await api.put(`/roles/${roleId.value}/permissions`, { permissions: payload });
    toast.success("权限已保存");
  } catch (error) {
    toast.error(error?.response?.data?.detail || "权限保存失败");
  }
};

const goBack = () => {
  router.push("/roles");
};

onMounted(async () => {
  await loadRole();
  await loadResources();
  await loadPermissions();
});
</script>

<style scoped></style>



