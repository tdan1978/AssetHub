<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增用户</h2>
          <p class="text-sm text-muted-foreground">创建新账号并分配角色。</p>
        </div>
        <RouterLink to="/users">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="grid gap-3 md:grid-cols-4">
        <Input v-model="form.username" placeholder="用户名" />
        <Input v-model="form.full_name" placeholder="姓名" />
        <Input v-model="form.dept" placeholder="部门" />
        <Select v-model="form.role_id">
          <SelectTrigger>
            <SelectValue placeholder="选择角色" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="role in roles" :key="role.id" :value="String(role.id)">
              {{ role.name }}
            </SelectItem>
          </SelectContent>
        </Select>
        <Input v-model="form.password" class="md:col-span-2" type="password" placeholder="密码" />
      </div>
      <div class="mt-4">
        <Button @click="save">保存</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

const router = useRouter();
const roles = ref([]);
const form = ref({ username: "", full_name: "", dept: "", role_id: "", password: "" });

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data;
};

const save = async () => {
  if (!form.value.username || !form.value.password || !form.value.role_id) return;
  await api.post("/users", { ...form.value, role_id: Number(form.value.role_id) });
  router.push("/users");
};

onMounted(loadRoles);
</script>
