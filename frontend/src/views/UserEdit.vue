<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑用户</h2>
          <p class="text-sm text-muted-foreground">修改用户信息与角色。</p>
        </div>
        <RouterLink to="/users">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-4">
        <div class="form-field">
          <label class="form-label">用户名</label>
          <Input v-model="form.username" placeholder="用户名" disabled />
        </div>
        <div class="form-field">
          <label class="form-label">姓名</label>
          <Input v-model="form.full_name" placeholder="姓名" />
        </div>
        <div class="form-field">
          <label class="form-label">部门</label>
          <Input v-model="form.dept" placeholder="部门" />
        </div>
        <div class="form-field">
          <label class="form-label">角色</label>
          <Select v-model="form.role_id">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择角色" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="role in roles" :key="role.id" :value="String(role.id)">
                {{ role.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field md:col-span-2">
          <label class="form-label">重置密码</label>
          <Input v-model="form.password" type="password" placeholder="重置密码(可选)" />
        </div>
      </div>
      <div class="mt-4">
        <Button @click="save">保存</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

const route = useRoute();
const router = useRouter();
const userId = Number(route.params.id);
const roles = ref([]);
const form = ref({ username: "", full_name: "", dept: "", role_id: "", password: "" });

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data;
};

const loadUser = async () => {
  const { data } = await api.get(`/users/${userId}`);
  form.value = { ...data, password: "" };
};

const save = async () => {
  const payload = {
    full_name: form.value.full_name,
    dept: form.value.dept,
    role_id: Number(form.value.role_id)
  };
  if (form.value.password) {
    payload.password = form.value.password;
  }
  await api.put(`/users/${userId}`, payload);
  router.push("/users");
};

onMounted(async () => {
  await loadRoles();
  await loadUser();
});
</script>
