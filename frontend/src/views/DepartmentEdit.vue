<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑部门</h2>
          <p class="text-sm text-muted-foreground">更新部门信息。</p>
        </div>
        <RouterLink to="/departments">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">部门名称</label>
          <Input v-model="form.name" placeholder="部门名称" />
        </div>
        <div class="form-field">
          <label class="form-label">部门编码</label>
          <Input v-model="form.code" placeholder="编码（可选）" />
        </div>
        <div class="form-field">
          <label class="form-label">上级部门</label>
          <Select v-model="form.parent_id">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择上级（可选）" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem :value="noneValue">无</SelectItem>
              <SelectItem v-for="item in parentOptions" :key="item.id" :value="String(item.id)">
                {{ item.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field">
          <label class="form-label">排序</label>
          <Input v-model="form.sort_order" type="number" placeholder="排序" />
        </div>
        <div class="form-field">
          <label class="form-label">状态</label>
          <div class="flex items-center gap-3 text-sm">
            <Switch v-model="form.is_active" />
            <span class="text-muted-foreground">启用</span>
          </div>
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
import { Switch } from "../components/ui/switch";

const route = useRoute();
const router = useRouter();
const deptId = Number(route.params.id);
const noneValue = "__none__";
const parentOptions = ref([]);
const form = ref({
  name: "",
  code: "",
  parent_id: noneValue,
  sort_order: 0,
  is_active: true
});

const load = async () => {
  const [{ data: dept }, { data: list }] = await Promise.all([
    api.get(`/departments/${deptId}`),
    api.get("/departments", { params: { page: 1, size: 500 } })
  ]);
  parentOptions.value = (list.items || []).filter((item) => item.id !== deptId);
  form.value = {
    name: dept.name,
    code: dept.code || "",
    parent_id: dept.parent_id ? String(dept.parent_id) : noneValue,
    sort_order: dept.sort_order || 0,
    is_active: Boolean(dept.is_active)
  };
};

const save = async () => {
  if (!form.value.name) return;
  await api.put(`/departments/${deptId}`, {
    name: form.value.name,
    code: form.value.code || null,
    parent_id: form.value.parent_id === noneValue ? null : Number(form.value.parent_id),
    sort_order: Number(form.value.sort_order || 0),
    is_active: Boolean(form.value.is_active)
  });
  router.push("/departments");
};

onMounted(load);
</script>



