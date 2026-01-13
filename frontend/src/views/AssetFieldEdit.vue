<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑字段</h2>
          <p class="text-sm text-muted-foreground">更新字段配置。</p>
        </div>
        <RouterLink :to="`/asset-types/${categoryId}/fields`">
          <Button variant="outline">返回字段</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="grid gap-3 md:grid-cols-2">
        <Input v-model="form.name" placeholder="字段名称" />
        <Input v-model="form.field_key" placeholder="字段键" />
        <Select v-model="form.field_type">
          <SelectTrigger>
            <SelectValue placeholder="字段类型" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="text">文本</SelectItem>
            <SelectItem value="textarea">多行文本</SelectItem>
            <SelectItem value="number">数字</SelectItem>
            <SelectItem value="date">日期</SelectItem>
            <SelectItem value="single_select">单选</SelectItem>
            <SelectItem value="multi_select">多选</SelectItem>
            <SelectItem value="boolean">布尔</SelectItem>
          </SelectContent>
        </Select>
        <Input v-model="options" placeholder="选项（单选/多选用逗号分隔）" />
        <div class="flex items-center gap-2 text-sm">
          <Checkbox v-model="form.is_required" />
          <span>必填</span>
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
import { Checkbox } from "../components/ui/checkbox";

const route = useRoute();
const router = useRouter();
const categoryId = Number(route.params.id);
const fieldId = Number(route.params.fieldId);
const options = ref("");
const form = ref({ name: "", field_key: "", field_type: "text", is_required: false, sort_order: 0 });

const load = async () => {
  const { data } = await api.get(`/categories/${categoryId}/fields`);
  const item = data.find((f) => f.id === fieldId);
  if (!item) return;
  form.value = { ...item };
  options.value = (item.options || []).join(",");
};

const save = async () => {
  await api.put(`/categories/fields/${fieldId}`, {
    ...form.value,
    options: options.value ? options.value.split(",").map((item) => item.trim()).filter(Boolean) : null
  });
  router.push(`/asset-types/${categoryId}/fields`);
};

onMounted(load);
</script>
