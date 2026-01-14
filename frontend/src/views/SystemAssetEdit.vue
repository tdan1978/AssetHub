<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑系统资产</h2>
          <p class="text-sm text-muted-foreground">更新系统基础信息与自定义字段。</p>
        </div>
        <RouterLink to="/systems">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card space-y-6">
      <div v-for="category in categories" :key="category.id" class="space-y-3" v-show="isCategoryVisible(category)">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold">{{ category.name }}</h3>
        </div>
        <div class="form-grid-2">
          <div v-for="field in category.fields" :key="field.id" class="form-field" v-show="shouldShowField(field)">
            <label class="form-label">
              {{ field.name }} <span v-if="field.is_required">*</span>
            </label>
            <Input v-if="field.field_type === 'text' && isBaseField(field)" v-model="form[field.field_key]" />
            <Input v-else-if="field.field_type === 'text'" v-model="fieldValues[field.id]" />
            <Textarea v-else-if="field.field_type === 'textarea' && isBaseField(field)" v-model="form[field.field_key]" />
            <Textarea v-else-if="field.field_type === 'textarea'" v-model="fieldValues[field.id]" />
            <Input v-else-if="field.field_type === 'number' && isBaseField(field)" v-model="form[field.field_key]" type="number" />
            <Input v-else-if="field.field_type === 'number'" v-model="fieldValues[field.id]" type="number" />
            <DatePicker v-else-if="field.field_type === 'date' && isBaseField(field)" v-model="form[field.field_key]" :showMonthYearSelect="true" />
            <DatePicker v-else-if="field.field_type === 'date'" v-model="fieldValues[field.id]" :showMonthYearSelect="true" />
            <Select v-else-if="field.field_type === 'single_select' && isBaseField(field)" v-model="form[field.field_key]">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="选择" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="opt in field.options || []" :key="opt" :value="opt">
                  {{ opt }}
                </SelectItem>
              </SelectContent>
            </Select>
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
              <Switch v-if="isBaseField(field)" v-model="form[field.field_key]" />
              <Switch v-else v-model="fieldValues[field.id]" />
              <span class="text-muted-foreground">是否</span>
            </div>
          </div>
        </div>
      </div>

      <div>
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
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Switch } from "../components/ui/switch";
import { DatePicker } from "../components/ui/date-picker";

const route = useRoute();
const router = useRouter();
const systemId = Number(route.params.id);
const categories = ref([]);
const fieldValues = ref({});
const form = ref({});
const activeBaseKeys = ref([]);
const customFields = ref([]);
const systemData = ref(null);

const baseFieldKeys = new Set([
  "app_name",
  "app_code",
  "app_status",
  "access_url",
  "app_category",
  "arch_type",
  "dev_lang",
  "db_type",
  "deploy_type",
  "repo_url",
  "biz_owner",
  "tech_owner",
  "ops_owner",
  "sec_level"
]);

const fieldMap = computed(() => {
  const map = new Map();
  for (const category of categories.value) {
    for (const field of category.fields || []) {
      map.set(field.id, field);
    }
  }
  return map;
});

const shouldShowField = (field) => {
  const rule = Array.isArray(field.visibility_rules) ? field.visibility_rules[0] : null;
  if (!rule || !rule.depends_on) return true;
  const dependsOnId = Number(rule.depends_on);
  if (!dependsOnId) return true;
  const dependsField = fieldMap.value.get(dependsOnId);
  if (!dependsField) return true;
  const currentValue = isBaseField(dependsField)
    ? form.value[dependsField.field_key]
    : fieldValues.value[dependsField.id];
  const matches = Array.isArray(currentValue)
    ? currentValue.map(String).includes(String(rule.value))
    : String(currentValue ?? "") === String(rule.value);
  return rule.action === "hide" ? !matches : matches;
};

const isCategoryVisible = (category) => (category.fields || []).some((field) => shouldShowField(field));

const loadSystem = async () => {
  const { data } = await api.get(`/systems/${systemId}`);
  systemData.value = data;
};

const loadFieldValues = async () => {
  const { data } = await api.get(`/systems/${systemId}/fields`);
  for (const item of data) {
    fieldValues.value[item.field_id] = item.value;
  }
};

const loadFields = async () => {
  const { data } = await api.get("/system-field-categories/tree");
  categories.value = data;
  fieldValues.value = {};
  activeBaseKeys.value = [];
  customFields.value = [];
  for (const category of categories.value) {
    for (const field of category.fields || []) {
      if (baseFieldKeys.has(field.field_key)) {
        activeBaseKeys.value.push(field.field_key);
        form.value[field.field_key] = systemData.value?.[field.field_key] || "";
      } else {
        customFields.value.push(field);
        if (field.field_type === "multi_select") {
          fieldValues.value[field.id] = [];
        } else if (field.field_type === "boolean") {
          fieldValues.value[field.id] = false;
        } else {
          fieldValues.value[field.id] = "";
        }
      }
    }
  }
  await loadFieldValues();
};

const toggleMultiSelect = (fieldId, option, checked) => {
  const current = Array.isArray(fieldValues.value[fieldId]) ? fieldValues.value[fieldId] : [];
  if (checked) {
    fieldValues.value[fieldId] = current.includes(option) ? current : [...current, option];
  } else {
    fieldValues.value[fieldId] = current.filter((item) => item !== option);
  }
};

const save = async () => {
  const basePayload = {};
  for (const key of activeBaseKeys.value) {
    basePayload[key] = form.value[key] ?? null;
  }
  await api.put(`/systems/${systemId}`, basePayload);
  if (customFields.value.length) {
    const payload = customFields.value.map((field) => ({
      field_id: field.id,
      value: fieldValues.value[field.id]
    }));
    await api.put(`/systems/${systemId}/fields`, payload);
  }
  router.push("/systems");
};

onMounted(async () => {
  await loadSystem();
  await loadFields();
});

const isBaseField = (field) => baseFieldKeys.has(field.field_key);
</script>
