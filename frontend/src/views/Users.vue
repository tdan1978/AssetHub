<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <Button @click="showCreate = !showCreate">
        {{ showCreate ? "收起新增" : "新增用户" }}
      </Button>
    </div>

    <div v-if="showCreate" class="rounded-lg border bg-background p-4">
      <h2 class="mb-4 text-base font-semibold">新增用户</h2>
      <div class="grid gap-3 md:grid-cols-4">
        <input v-model="form.username" class="input" placeholder="用户名" />
        <input v-model="form.full_name" class="input" placeholder="姓名" />
        <input v-model="form.dept" class="input" placeholder="部门" />
        <select v-model="form.role_id" class="input">
          <option value="">选择角色</option>
          <option v-for="role in roles" :key="role.id" :value="role.id">
            {{ role.name }}
          </option>
        </select>
        <input v-model="form.password" class="input md:col-span-2" type="password" placeholder="密码" />
        <div class="md:col-span-2">
          <Button @click="create">保存</Button>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <table class="w-full text-sm">
        <thead class="border-b bg-muted/40 text-left">
          <tr>
            <th class="px-4 py-2">ID</th>
            <th class="px-4 py-2">用户名</th>
            <th class="px-4 py-2">姓名</th>
            <th class="px-4 py-2">角色</th>
            <th class="px-4 py-2">部门</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.id }}</td>
            <td class="px-4 py-2">{{ item.username }}</td>
            <td class="px-4 py-2">{{ item.full_name }}</td>
            <td class="px-4 py-2">{{ roleMap[item.role_id] || item.role_id }}</td>
            <td class="px-4 py-2">{{ item.dept }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";

const items = ref([]);
const roles = ref([]);
const showCreate = ref(false);
const form = ref({
  username: "",
  full_name: "",
  dept: "",
  role_id: "",
  password: ""
});

const roleMap = computed(() => {
  const map = {};
  for (const role of roles.value) {
    map[role.id] = role.name;
  }
  return map;
});

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data;
};

const loadUsers = async () => {
  const { data } = await api.get("/users", { params: { page: 1, size: 50 } });
  items.value = data.items;
};

const create = async () => {
  if (!form.value.username || !form.value.password || !form.value.role_id) return;
  const payload = {
    ...form.value,
    role_id: Number(form.value.role_id)
  };
  await api.post("/users", payload);
  form.value = { username: "", full_name: "", dept: "", role_id: "", password: "" };
  showCreate.value = false;
  await loadUsers();
};

onMounted(async () => {
  await loadRoles();
  await loadUsers();
});
</script>

<style scoped></style>
