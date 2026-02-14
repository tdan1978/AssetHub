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
          <Select v-model="selectedDept">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择部门" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__none__">未选择</SelectItem>
              <SelectItem v-for="item in departmentOptions" :key="item.value" :value="String(item.value)">
                {{ item.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field">
          <label class="form-label">电话</label>
          <Input v-model="form.phone" placeholder="手机号" />
        </div>
        <div class="form-field">
          <label class="form-label">企业微信名</label>
          <Input v-model="form.wecom_name" placeholder="企业微信名" />
        </div>
        <div class="form-field">
          <label class="form-label">角色</label>
          <Select v-model="form.role_ids" multiple>
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择角色" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="role in roles" :key="role.id" :value="role.id">
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
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";

const route = useRoute();
const router = useRouter();
const userId = Number(route.params.id);
const roles = ref([]);
const departmentOptions = ref([]);
const form = ref({ username: "", full_name: "", dept: "", phone: "", wecom_name: "", role_ids: [], password: "" });

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data;
};

const loadDepartments = async () => {
  try {
    const { data } = await api.get("/departments/options");
    departmentOptions.value = Array.isArray(data) ? data : [];
  } catch {
    departmentOptions.value = [];
  }
};

const loadUser = async () => {
  const { data } = await api.get(`/users/${userId}`);
  form.value = {
    ...data,
    phone: data.phone || "",
    wecom_name: data.wecom_name || "",
    role_ids: data.role_ids || [],
    password: ""
  };
};

const selectedDept = computed({
  get: () => {
    const current = String(form.value.dept || "").trim();
    if (!current) return "__none__";
    const matched = departmentOptions.value.find(
      (item) => String(item?.value) === current || String(item?.label || "").trim() === current
    );
    return matched ? String(matched.value) : "__none__";
  },
  set: (value) => {
    const normalized = String(value || "");
    if (!normalized || normalized === "__none__") {
      form.value.dept = "";
      return;
    }
    const matched = departmentOptions.value.find((item) => String(item?.value) === normalized);
    form.value.dept = matched ? String(matched.label || "").trim() : "";
  },
});

const save = async () => {
  const payload = {
    full_name: form.value.full_name,
    dept: form.value.dept,
    phone: form.value.phone || null,
    wecom_name: form.value.wecom_name || null,
    role_ids: form.value.role_ids
  };
  if (form.value.password) {
    payload.password = form.value.password;
  }
  await api.put(`/users/${userId}`, payload);
  router.push("/users");
};

onMounted(async () => {
  await Promise.all([loadRoles(), loadDepartments(), loadUser()]);
});
</script>



