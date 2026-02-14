<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增字段分类</h2>
          <p class="text-sm text-muted-foreground">为系统字段创建分类。</p>
        </div>
        <RouterLink to="/system-field-categories">
          <Button variant="outline">返回分类</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">分类名称</label>
          <Input v-model="form.name" placeholder="分类名称" />
        </div>
        <div class="form-field">
          <label class="form-label">分类编码</label>
          <Input v-model="form.code" placeholder="分类编码" />
        </div>
        <div class="form-field">
          <label class="form-label">排序</label>
          <Input v-model="form.sort_order" type="number" placeholder="排序" />
        </div>
        <div class="form-field">
          <label class="form-label">描述</label>
          <Input v-model="form.description" placeholder="描述" />
        </div>
      </div>
      <div class="mt-4">
        <Button @click="save">保存</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

const router = useRouter();
const form = ref({ name: "", code: "", description: "", sort_order: 0, is_active: true });

const save = async () => {
  if (!form.value.name) return;
  await api.post("/system-field-categories", form.value);
  router.push("/system-field-categories");
};
</script>



