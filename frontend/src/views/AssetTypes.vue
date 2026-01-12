<template>
  <div class="space-y-6">
    <div class="card">
      <h2 class="text-base font-semibold">资产类型与字段配置</h2>
      <p class="mt-1 text-sm text-muted-foreground">
        先创建资产类型，再为该类型配置字段（文本、单选、多选等）。
      </p>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <div class="card">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold">资产类型</h3>
          <Button variant="outline" @click="showCategory = !showCategory">
            {{ showCategory ? "收起新增" : "新增类型" }}
          </Button>
        </div>

        <div v-if="showCategory" class="mt-4 grid gap-2">
          <input v-model="categoryForm.name" class="input" placeholder="类型名称" />
          <input v-model="categoryForm.code" class="input" placeholder="类型编码" />
          <input v-model="categoryForm.description" class="input" placeholder="描述" />
          <Button @click="createCategory">保存</Button>
        </div>

        <table class="table mt-4">
          <thead>
            <tr>
              <th>名称</th>
              <th>编码</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in categories" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.code || '-' }}</td>
              <td>{{ item.is_active ? '启用' : '停用' }}</td>
              <td>
                <Button size="sm" variant="outline" @click="selectCategory(item)">字段配置</Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-semibold">字段配置</h3>
            <p class="text-xs text-muted-foreground">当前类型：{{ currentCategory?.name || "未选择" }}</p>
          </div>
          <Button variant="outline" :disabled="!currentCategory" @click="showField = !showField">
            {{ showField ? "收起新增" : "新增字段" }}
          </Button>
        </div>

        <div v-if="showField" class="mt-4 grid gap-2">
          <input v-model="fieldForm.name" class="input" placeholder="字段名称" />
          <input v-model="fieldForm.field_key" class="input" placeholder="字段键" />
          <select v-model="fieldForm.field_type" class="input">
            <option value="text">文本</option>
            <option value="textarea">多行文本</option>
            <option value="number">数字</option>
            <option value="date">日期</option>
            <option value="single_select">单选</option>
            <option value="multi_select">多选</option>
            <option value="boolean">布尔</option>
          </select>
          <input v-model="fieldOptions" class="input" placeholder="选项（单选/多选用逗号分隔）" />
          <label class="text-xs text-muted-foreground">
            <input v-model="fieldForm.is_required" type="checkbox" /> 必填
          </label>
          <Button :disabled="!currentCategory" @click="createField">保存</Button>
        </div>

        <table class="table mt-4">
          <thead>
            <tr>
              <th>名称</th>
              <th>键</th>
              <th>类型</th>
              <th>必填</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in fields" :key="item.id">
              <td>{{ item.name }}</td>
              <td>{{ item.field_key }}</td>
              <td>{{ item.field_type }}</td>
              <td>{{ item.is_required ? '是' : '否' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";

const categories = ref([]);
const fields = ref([]);
const currentCategory = ref(null);
const showCategory = ref(false);
const showField = ref(false);

const categoryForm = ref({ name: "", code: "", description: "" });
const fieldForm = ref({ name: "", field_key: "", field_type: "text", is_required: false });
const fieldOptions = ref("");

const loadCategories = async () => {
  const { data } = await api.get("/categories");
  categories.value = data;
};

const selectCategory = async (item) => {
  currentCategory.value = item;
  showField.value = false;
  const { data } = await api.get(`/categories/${item.id}/fields`);
  fields.value = data;
};

const createCategory = async () => {
  if (!categoryForm.value.name) return;
  await api.post("/categories", categoryForm.value);
  categoryForm.value = { name: "", code: "", description: "" };
  showCategory.value = false;
  await loadCategories();
};

const createField = async () => {
  if (!currentCategory.value || !fieldForm.value.name || !fieldForm.value.field_key) return;
  const payload = {
    ...fieldForm.value,
    options: fieldOptions.value
      ? fieldOptions.value.split(",").map((item) => item.trim()).filter(Boolean)
      : null
  };
  await api.post(`/categories/${currentCategory.value.id}/fields`, payload);
  fieldForm.value = { name: "", field_key: "", field_type: "text", is_required: false };
  fieldOptions.value = "";
  showField.value = false;
  await selectCategory(currentCategory.value);
};

onMounted(loadCategories);
</script>

<style scoped></style>
