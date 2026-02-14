<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑人员</h2>
          <p class="text-sm text-muted-foreground">更新人员基本信息。</p>
        </div>
        <RouterLink to="/people">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">姓名</label>
          <Input v-model="form.name" placeholder="姓名" />
        </div>
        <div class="form-field">
          <label class="form-label">工号</label>
          <Input v-model="form.emp_code" placeholder="工号（可选）" />
        </div>
        <div class="form-field">
          <label class="form-label">部门</label>
          <Select v-model="form.dept_id">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择部门" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem :value="noneValue">无</SelectItem>
              <SelectItem v-for="item in departments" :key="item.id" :value="String(item.id)">
                {{ item.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field">
          <label class="form-label">手机号</label>
          <Input v-model="form.phone" placeholder="手机号" />
        </div>
        <div class="form-field">
          <label class="form-label">邮箱</label>
          <Input v-model="form.email" placeholder="邮箱" />
        </div>
        <div class="form-field">
          <label class="form-label">状态</label>
          <Select v-model="form.status">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="在职">在职</SelectItem>
              <SelectItem value="离职">离职</SelectItem>
              <SelectItem value="停用">停用</SelectItem>
            </SelectContent>
          </Select>
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
const personId = Number(route.params.id);
const noneValue = "__none__";
const departments = ref([]);
const form = ref({
  name: "",
  emp_code: "",
  dept_id: noneValue,
  phone: "",
  email: "",
  status: "在职"
});

const load = async () => {
  const [{ data: person }, { data: deptData }] = await Promise.all([
    api.get(`/people/${personId}`),
    api.get("/departments", { params: { page: 1, size: 500 } })
  ]);
  departments.value = deptData.items || [];
  form.value = {
    name: person.name,
    emp_code: person.emp_code || "",
    dept_id: person.dept_id ? String(person.dept_id) : noneValue,
    phone: person.phone || "",
    email: person.email || "",
    status: person.status || "在职"
  };
};

const save = async () => {
  if (!form.value.name) return;
  await api.put(`/people/${personId}`, {
    name: form.value.name,
    emp_code: form.value.emp_code || null,
    dept_id: form.value.dept_id === noneValue ? null : Number(form.value.dept_id),
    phone: form.value.phone || null,
    email: form.value.email || null,
    status: form.value.status || null
  });
  router.push("/people");
};

onMounted(load);
</script>



