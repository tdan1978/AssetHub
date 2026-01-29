<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增资产</h2>
          <p class="text-sm text-muted-foreground">填写基础信息与自定义字段。</p>
        </div>
        <RouterLink to="/assets">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-4">
        <div class="form-field">
          <label class="form-label">SN</label>
          <Input v-model="form.sn" placeholder="SN" />
        </div>
        <div class="form-field">
          <label class="form-label">编号</label>
          <Input v-model="form.asset_no" placeholder="自动生成" disabled />
        </div>
        <div class="form-field">
          <label class="form-label">名称</label>
          <Input v-model="form.name" placeholder="名称" />
        </div>
        <div class="form-field">
          <label class="form-label">资产类型</label>
          <Select v-model="form.category_id" @update:modelValue="onCategoryChange">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择类型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="item in categories" :key="item.id" :value="item.id">
                {{ item.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field">
          <label class="form-label">用途</label>
          <Select v-model="form.dept">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择用途" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="办公和业务">办公和业务</SelectItem>
              <SelectItem value="数据中心">数据中心</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div v-show="fields.length" class="mt-6 form-grid-2">
        <div v-for="field in fields" :key="field.id" class="form-field" v-show="shouldShowField(field)">
          <label class="form-label">
            {{ field.name }} <span v-if="field.is_required">*</span>
          </label>
          <Input v-if="field.field_type === 'text'" v-model="fieldValues[field.id]" />
          <Textarea v-else-if="field.field_type === 'textarea'" v-model="fieldValues[field.id]" />
          <Input v-else-if="field.field_type === 'number'" v-model="fieldValues[field.id]" type="number" />
          <DatePicker v-else-if="field.field_type === 'date'" v-model="fieldValues[field.id]" :showMonthYearSelect="true" />
          <Select v-else-if="field.field_type === 'single_select'" v-model="fieldValues[field.id]">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="opt in field.options || []" :key="opt" :value="opt">
                {{ opt }}
              </SelectItem>
            </SelectContent>
          </Select>
          <div v-else-if="field.field_type === 'multi_select'" class="grid gap-2">
            <label v-for="opt in field.options || []" :key="opt" class="flex items-center gap-2 text-sm">
              <Checkbox
                :modelValue="fieldValues[field.id]?.includes(opt)"
                @update:modelValue="(checked) => toggleMultiSelect(field.id, opt, checked)"
              />
              <span>{{ opt }}</span>
            </label>
          </div>
          <div v-else-if="field.field_type === 'boolean'" class="flex items-center gap-3 text-sm">
            <Switch v-model="fieldValues[field.id]" />
            <span class="text-muted-foreground">是否</span>
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
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Switch } from "../components/ui/switch";
import { DatePicker } from "../components/ui/date-picker";

const router = useRouter();
const categories = ref([]);
const fields = ref([]);
const fieldValues = ref({});
const form = ref({
  sn: "",
  asset_no: "",
  name: "",
  category: "",
  category_id: null,
  dept: "",
  status: 0
});

const loadCategories = async () => {
  const { data } = await api.get("/categories");
  categories.value = data;
};

const onCategoryChange = async () => {
  fields.value = [];
  fieldValues.value = {};
  const categoryId = Number(form.value.category_id);
  form.value.category_id = Number.isNaN(categoryId) ? null : categoryId;
  const category = categories.value.find((item) => item.id === form.value.category_id);
  form.value.category = category?.name || "";
  if (!form.value.category_id) return;
  const { data } = await api.get(`/categories/${form.value.category_id}/fields`);
  fields.value = data;
  for (const field of fields.value) {
    if (field.field_type === "multi_select") {
      fieldValues.value[field.id] = [];
    } else if (field.field_type === "boolean") {
      fieldValues.value[field.id] = false;
    } else {
      fieldValues.value[field.id] = "";
    }
  }
};

const toggleMultiSelect = (fieldId, option, checked) => {
  const current = Array.isArray(fieldValues.value[fieldId]) ? fieldValues.value[fieldId] : [];
  if (checked) {
    fieldValues.value[fieldId] = current.includes(option) ? current : [...current, option];
  } else {
    fieldValues.value[fieldId] = current.filter((item) => item !== option);
  }
};

const shouldShowField = (field) => {
  const rule = Array.isArray(field.visibility_rules) ? field.visibility_rules[0] : null;
  if (!rule || !rule.depends_on) return true;
  const depId = Number(rule.depends_on);
  if (!depId) return true;
  const currentValue = fieldValues.value[depId];
  const matches = Array.isArray(currentValue)
    ? currentValue.map(String).includes(String(rule.value))
    : String(currentValue ?? "") === String(rule.value);
  return rule.action === "hide" ? !matches : matches;
};

const save = async () => {
  const { data } = await api.post("/assets", form.value);
  if (fields.value.length) {
    const payload = fields.value.map((field) => ({
      field_id: field.id,
      value: fieldValues.value[field.id]
    }));
    await api.put(`/assets/${data.id}/fields`, payload);
  }
  router.push("/assets");
};

onMounted(loadCategories);
</script>
