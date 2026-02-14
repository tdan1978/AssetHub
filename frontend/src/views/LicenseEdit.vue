<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑软件资产</h2>
          <p class="text-sm text-muted-foreground">更新软件基础信息与自定义字段。</p>
        </div>
        <div class="flex gap-2">
          <RouterLink to="/licenses">
            <Button variant="outline">返回列表</Button>
          </RouterLink>
          <Button @click="save">保存</Button>
        </div>
      </div>
    </div>

    <div class="card space-y-6">
      <div v-for="category in categories" :key="category.id" class="space-y-3" v-show="isCategoryVisible(category)">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold">{{ category.name }}</h3>
        </div>
        <div class="form-grid-2 xl:grid-cols-3 form-grid-divider-md-2-xl-3">
          <div
            v-for="field in category.fields"
            :key="field.id"
            :class="[
              'form-field',
              field.field_type === 'multi_select' && field.multi_select_mode === 'tags'
                ? 'form-field-span-all md:col-span-2 xl:col-span-3'
                : ''
            ]"
            v-show="shouldShowField(field)"
          >
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
            <Combobox
              v-else-if="field.field_type === 'combo_select' && isBaseField(field)"
              v-model="form[field.field_key]"
              :options="getFieldOptions(field)"
              placeholder="选择"
            />
            <Combobox
              v-else-if="field.field_type === 'combo_select'"
              v-model="fieldValues[field.id]"
              :options="getFieldOptions(field)"
              placeholder="选择"
            />
            <Select v-else-if="field.field_type === 'single_select' && isBaseField(field)" v-model="form[field.field_key]">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="选择" />
              </SelectTrigger>
              <SelectContent class="max-h-72 overflow-y-auto">
                <div v-if="isFieldSearchable(field)" class="px-2 pb-2">
                  <Input
                    :model-value="getFieldOptionKeyword(field.id)"
                    class="h-8"
                    placeholder="搜索选项"
                    @keydown.stop
                    @update:modelValue="(value) => setFieldOptionKeyword(field.id, value)"
                  />
                </div>
                <SelectItem v-for="opt in getDisplayFieldOptions(field)" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </SelectItem>
              </SelectContent>
            </Select>
            <Select v-else-if="field.field_type === 'single_select'" v-model="fieldValues[field.id]">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="选择" />
              </SelectTrigger>
              <SelectContent class="max-h-72 overflow-y-auto">
                <div v-if="isFieldSearchable(field)" class="px-2 pb-2">
                  <Input
                    :model-value="getFieldOptionKeyword(field.id)"
                    class="h-8"
                    placeholder="搜索选项"
                    @keydown.stop
                    @update:modelValue="(value) => setFieldOptionKeyword(field.id, value)"
                  />
                </div>
                <SelectItem v-for="opt in getDisplayFieldOptions(field)" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </SelectItem>
              </SelectContent>
            </Select>
            <div v-else-if="field.field_type === 'compound'" class="rounded-md border p-3 space-y-3">
              <div
                v-for="(row, index) in fieldValues[field.id]"
                :key="index"
                class="rounded-md border border-dashed p-2"
              >
                <div class="flex items-start gap-2">
                  <div class="grid flex-1 gap-3 md:grid-cols-[repeat(auto-fit,minmax(180px,1fr))]">
                    <div v-for="sub in getCompoundFields(field)" :key="sub.key" class="flex items-center gap-1">
                      <span class="w-12 shrink-0 text-xs text-muted-foreground">{{ sub.name }}</span>
                    <Input
                      v-if="sub.type === 'text'"
                      v-model="fieldValues[field.id][index][sub.key]"
                      class="h-8 flex-1"
                    />
                    <Textarea
                      v-else-if="sub.type === 'textarea'"
                      v-model="fieldValues[field.id][index][sub.key]"
                      class="min-h-[36px] flex-1"
                    />
                    <div v-else-if="sub.type === 'markdown'" class="flex-1 space-y-1">
                      <Button
                        size="sm"
                        variant="outline"
                        type="button"
                        @click="openCompoundMarkdownEditor(field, index, sub)"
                      >
                        编辑文档
                      </Button>
                      <p class="text-xs text-muted-foreground">
                        {{ markdownSummary(fieldValues[field.id][index][sub.key]) }}
                      </p>
                    </div>
                    <Input
                      v-else-if="sub.type === 'number'"
                      v-model="fieldValues[field.id][index][sub.key]"
                      type="number"
                      class="h-8 flex-1"
                    />
                    <DatePicker
                      v-else-if="sub.type === 'date'"
                      v-model="fieldValues[field.id][index][sub.key]"
                      :showMonthYearSelect="true"
                      class="flex-1"
                    />
                    <Select v-else-if="sub.type === 'single_select'" v-model="fieldValues[field.id][index][sub.key]">
                      <SelectTrigger class="h-8 flex-1">
                        <SelectValue placeholder="选择" />
                      </SelectTrigger>
                      <SelectContent class="max-h-72 overflow-y-auto">
                        <SelectItem
                          v-for="opt in getCompoundSubOptions(sub)"
                          :key="`${sub.key}-${opt.value}`"
                          :value="opt.value"
                        >
                          {{ opt.label }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <Select
                      v-else-if="sub.type === 'multi_select'"
                      v-model="fieldValues[field.id][index][sub.key]"
                      multiple
                    >
                      <SelectTrigger class="h-8 flex-1">
                        <SelectValue placeholder="选择" />
                      </SelectTrigger>
                      <SelectContent class="max-h-72 overflow-y-auto">
                        <SelectItem
                          v-for="opt in getCompoundSubOptions(sub)"
                          :key="`${sub.key}-${opt.value}`"
                          :value="opt.value"
                        >
                          {{ opt.label }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <div v-else-if="sub.type === 'boolean'" class="flex h-8 flex-1 items-center gap-2">
                      <Switch
                        :model-value="Boolean(fieldValues[field.id][index][sub.key])"
                        @update:model-value="(value) => (fieldValues[field.id][index][sub.key] = Boolean(value))"
                      />
                      <span class="text-xs text-muted-foreground">
                        {{ fieldValues[field.id][index][sub.key] ? "是" : "否" }}
                      </span>
                    </div>
                      <Input v-else v-model="fieldValues[field.id][index][sub.key]" class="h-8 flex-1" />
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    type="button"
                    :disabled="fieldValues[field.id].length <= 1"
                    @click="removeCompoundRow(field.id, index, field)"
                  >
                    删除
                  </Button>
                </div>
              </div>
              <Button size="sm" variant="outline" type="button" @click="addCompoundRow(field.id, field)">
                + 添加一行
              </Button>
            </div>
            <div v-else-if="field.field_type === 'multi_select' && field.multi_select_mode === 'tags'" class="space-y-2">
              <Input
                v-if="isFieldSearchable(field)"
                :model-value="getFieldOptionKeyword(field.id)"
                class="h-8"
                placeholder="搜索选项"
                @update:modelValue="(value) => setFieldOptionKeyword(field.id, value)"
              />
              <div class="max-h-56 overflow-y-auto pr-1">
                <ToggleGroup v-model="fieldValues[field.id]" type="multiple">
                  <ToggleGroupItem
                    v-for="opt in getDisplayFieldOptions(field)"
                    :key="opt.value"
                    :value="opt.value"
                    :show-check="true"
                    :muted-when-inactive="true"
                    :inactive-dot="true"
                    class="rounded-full px-3 py-1 text-xs"
                  >
                    {{ opt.label }}
                  </ToggleGroupItem>
                </ToggleGroup>
              </div>
            </div>
            <Select v-else-if="field.field_type === 'multi_select'" v-model="fieldValues[field.id]" multiple>
              <SelectTrigger class="w-full">
                <SelectValue placeholder="选择" />
              </SelectTrigger>
              <SelectContent class="max-h-72 overflow-y-auto">
                <div v-if="isFieldSearchable(field)" class="px-2 pb-2">
                  <Input
                    :model-value="getFieldOptionKeyword(field.id)"
                    class="h-8"
                    placeholder="搜索选项"
                    @keydown.stop
                    @update:modelValue="(value) => setFieldOptionKeyword(field.id, value)"
                  />
                </div>
                <SelectItem v-for="opt in getDisplayFieldOptions(field)" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </SelectItem>
              </SelectContent>
            </Select>
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

    <Dialog v-model:open="compoundMarkdownEditorOpen">
      <DialogContent class="w-[98vw] max-w-[min(98vw,1400px)] sm:max-w-[min(98vw,1400px)] md:max-w-[min(98vw,1400px)]">
        <DialogHeader>
          <DialogTitle>{{ compoundMarkdownEditorTitle }}</DialogTitle>
          <DialogDescription>支持 Markdown 文档编辑。</DialogDescription>
        </DialogHeader>
        <MdEditor v-model="compoundMarkdownDraft" language="zh-CN" style="height: 62vh" />
        <DialogFooter>
          <Button type="button" variant="outline" @click="compoundMarkdownEditorOpen = false">取消</Button>
          <Button type="button" @click="saveCompoundMarkdownDraft">保存文档</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Switch } from "../components/ui/switch";
import { DatePicker } from "../components/ui/date-picker";
import { ToggleGroup, ToggleGroupItem } from "../components/ui/toggle-group";
import { Combobox } from "../components/ui/combobox";
const MdEditor = defineAsyncComponent(async () => {
  await import("md-editor-v3/lib/style.css");
  const mod = await import("md-editor-v3");
  return mod.MdEditor;
});

const route = useRoute();
const router = useRouter();
const licenseId = Number(route.params.id);
const categories = ref([]);
const fieldValues = ref({});
const form = ref({});
const activeBaseKeys = ref([]);
const customFields = ref([]);
const licenseData = ref(null);
const departmentOptions = ref([]);
const peopleOptions = ref([]);
const userOptions = ref([]);
const dictOptions = ref({});
const fieldOptionKeyword = ref({});
const compoundMarkdownEditorOpen = ref(false);
const compoundMarkdownDraft = ref("");
const currentCompoundMarkdownContext = ref(null);

const baseFieldKeys = new Set([
  "software_name",
  "version",
  "vendor",
  "category",
  "vendor_url",
  "license_type",
  "billing_mode",
  "license_key",
  "total_quantity",
  "used_quantity",
  "activation_limit",
  "expiry_type",
  "expire_at",
  "renewal_at",
  "compliance_status",
  "cost",
  "purchase_date",
  "order_no",
  "supplier"
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
const compoundMarkdownEditorTitle = computed(() => {
  const ctx = currentCompoundMarkdownContext.value;
  if (!ctx) return "Markdown 文档";
  return `${ctx.fieldName} / 第${ctx.rowIndex + 1}行 / ${ctx.subName}`;
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

const loadLicense = async () => {
  const { data } = await api.get(`/licenses/${licenseId}`);
  licenseData.value = data;
};

const loadFieldValues = async () => {
  const { data } = await api.get(`/licenses/${licenseId}/fields`);
  for (const item of data) {
    fieldValues.value[item.field_id] = item.value;
  }
  for (const field of customFields.value) {
    if (field.field_type !== "multi_select") continue;
    const current = fieldValues.value[field.id];
    if (!Array.isArray(current)) {
      fieldValues.value[field.id] = current ? [current] : [];
    }
    if (Array.isArray(fieldValues.value[field.id])) {
      fieldValues.value[field.id] = fieldValues.value[field.id].map((item) => String(item));
    }
  }
  for (const field of customFields.value) {
    if (field.field_type !== "compound") continue;
    const current = fieldValues.value[field.id];
    if (!Array.isArray(current) || current.length === 0) {
      fieldValues.value[field.id] = [initCompoundRow(field)];
      continue;
    }
    fieldValues.value[field.id] = current.map((row) => ({
      ...initCompoundRow(field),
      ...(row || {})
    }));
  }
};

const loadFields = async () => {
  const { data } = await api.get("/software-field-categories/tree");
  categories.value = data;
  fieldValues.value = {};
  activeBaseKeys.value = [];
  customFields.value = [];
  for (const category of categories.value) {
    for (const field of category.fields || []) {
      if (baseFieldKeys.has(field.field_key)) {
        activeBaseKeys.value.push(field.field_key);
        form.value[field.field_key] = licenseData.value?.[field.field_key] ?? "";
      } else {
        customFields.value.push(field);
        if (field.field_type === "compound") {
          fieldValues.value[field.id] = [initCompoundRow(field)];
        } else if (field.field_type === "multi_select") {
          fieldValues.value[field.id] = [];
        } else if (field.field_type === "boolean") {
          fieldValues.value[field.id] = false;
        } else {
          fieldValues.value[field.id] = "";
        }
      }
    }
  }
  await preloadDictOptions(customFields.value);
  await loadFieldValues();
};

const isBaseField = (field) => baseFieldKeys.has(field.field_key);

const loadDepartmentOptions = async () => {
  try {
    const { data } = await api.get("/departments/options");
    departmentOptions.value = Array.isArray(data) ? data : [];
  } catch {
    departmentOptions.value = [];
  }
};

const loadPeopleOptions = async () => {
  try {
    const { data } = await api.get("/people/options");
    peopleOptions.value = Array.isArray(data) ? data : [];
  } catch {
    peopleOptions.value = [];
  }
};

const loadUserOptions = async () => {
  try {
    const { data } = await api.get("/users/options");
    userOptions.value = Array.isArray(data) ? data : [];
  } catch {
    userOptions.value = [];
  }
};

const loadDictOptions = async (code) => {
  if (!code || dictOptions.value[code]) return;
  try {
    const { data } = await api.get("/dictionaries/items", { params: { type: code } });
    const items = Array.isArray(data) ? data : [];
    dictOptions.value[code] = items
      .filter((item) => item.is_active !== false && String(item.name || "").trim() !== "")
      .map((item) => {
        const raw = String(item.value ?? "").trim();
        const fallback = String(item.name || "").trim();
        return { value: raw || fallback, label: item.name };
      })
      .filter((item) => item.value !== "");
  } catch {
    dictOptions.value[code] = [];
  }
};

const preloadDictOptions = async (fieldList) => {
  const codes = new Set();
  fieldList.forEach((field) => {
    if (field.data_source && field.data_source.startsWith("dict:")) {
      const code = field.data_source.replace("dict:", "");
      if (code) codes.add(code);
    }
  });
  await Promise.all([...codes].map((code) => loadDictOptions(code)));
};

const getFieldOptions = (field) => {
  if (field.field_type !== "single_select" && field.field_type !== "combo_select" && field.field_type !== "multi_select") return [];
  if (field.data_source === "departments") {
    return departmentOptions.value
      .filter((item) => item && item.value !== "" && item.value !== null && item.value !== undefined)
      .map((item) => ({
        value: String(item.value),
        label: item.label ?? String(item.value)
      }));
  }
  if (field.data_source === "people") {
    return peopleOptions.value
      .filter((item) => item && item.value !== "" && item.value !== null && item.value !== undefined)
      .map((item) => ({
        value: String(item.value),
        label: item.label ?? String(item.value)
      }));
  }
  if (field.data_source === "users") {
    return userOptions.value
      .filter((item) => item && item.value !== "" && item.value !== null && item.value !== undefined)
      .map((item) => ({
        value: String(item.value),
        label: item.label ?? String(item.value)
      }));
  }
  if (field.data_source && field.data_source.startsWith("dict:")) {
    const code = field.data_source.replace("dict:", "");
    if (code && !dictOptions.value[code]) {
      loadDictOptions(code);
    }
    return dictOptions.value[code] || [];
  }
  const options = Array.isArray(field.options) ? field.options : [];
  return options
    .filter((opt) => opt !== "" && opt !== null && opt !== undefined)
    .map((opt) => ({ value: String(opt), label: String(opt) }));
};

const getFieldOptionKeyword = (fieldId) => String(fieldOptionKeyword.value[fieldId] || "");

const setFieldOptionKeyword = (fieldId, keyword) => {
  fieldOptionKeyword.value[fieldId] = String(keyword || "");
};

const getFilteredFieldOptions = (field) => {
  const options = getFieldOptions(field);
  const keyword = getFieldOptionKeyword(field.id).trim().toLowerCase();
  if (!keyword) return options;
  return options.filter((opt) => String(opt.label ?? opt.value ?? "").toLowerCase().includes(keyword));
};

const isFieldSearchable = (field) => Boolean(field?.searchable) || field?.field_type === "combo_select";

const getDisplayFieldOptions = (field) => (isFieldSearchable(field) ? getFilteredFieldOptions(field) : getFieldOptions(field));

const getCompoundFields = (field) => (Array.isArray(field.options) ? field.options : []);
const getCompoundSubOptions = (sub) => {
  if (!Array.isArray(sub?.options)) return [];
  return sub.options
    .map((opt) => {
      if (opt && typeof opt === "object") {
        const value = String(opt.value ?? opt.label ?? "").trim();
        const label = String(opt.label ?? opt.value ?? "").trim();
        return { label: label || value, value };
      }
      const value = String(opt ?? "").trim();
      return { label: value, value };
    })
    .filter((opt) => opt.value);
};

const initCompoundRow = (field) => {
  const row = {};
  for (const sub of getCompoundFields(field)) {
    if (sub.type === "multi_select") {
      row[sub.key] = [];
    } else if (sub.type === "boolean") {
      row[sub.key] = false;
    } else {
      row[sub.key] = "";
    }
  }
  return row;
};

const addCompoundRow = (fieldId, field) => {
  const current = Array.isArray(fieldValues.value[fieldId]) ? fieldValues.value[fieldId] : [];
  fieldValues.value[fieldId] = [...current, initCompoundRow(field)];
};

const removeCompoundRow = (fieldId, index, field) => {
  const current = Array.isArray(fieldValues.value[fieldId]) ? fieldValues.value[fieldId] : [];
  const next = current.filter((_, i) => i !== index);
  fieldValues.value[fieldId] = next.length ? next : [initCompoundRow(field)];
};

const markdownSummary = (value) => {
  const text = String(value || "").trim();
  return text ? `已填写，${text.length} 字符` : "未填写";
};

const openCompoundMarkdownEditor = (field, rowIndex, sub) => {
  currentCompoundMarkdownContext.value = {
    fieldId: field.id,
    fieldName: field.name,
    rowIndex,
    subKey: sub.key,
    subName: sub.name || sub.key
  };
  const currentValue = fieldValues.value?.[field.id]?.[rowIndex]?.[sub.key];
  compoundMarkdownDraft.value = String(currentValue || "");
  compoundMarkdownEditorOpen.value = true;
};

const saveCompoundMarkdownDraft = () => {
  const ctx = currentCompoundMarkdownContext.value;
  if (!ctx) return;
  const rows = Array.isArray(fieldValues.value[ctx.fieldId]) ? fieldValues.value[ctx.fieldId] : [];
  if (!rows[ctx.rowIndex]) return;
  rows[ctx.rowIndex][ctx.subKey] = compoundMarkdownDraft.value || "";
  fieldValues.value[ctx.fieldId] = [...rows];
  compoundMarkdownEditorOpen.value = false;
};

const save = async () => {
  const basePayload = {};
  for (const key of activeBaseKeys.value) {
    basePayload[key] = form.value[key] ?? null;
  }
  await api.put(`/licenses/${licenseId}`, basePayload);
  if (customFields.value.length) {
    const payload = customFields.value.map((field) => ({
      field_id: field.id,
      value: fieldValues.value[field.id]
    }));
    await api.put(`/licenses/${licenseId}/fields`, payload);
  }
  router.push("/licenses");
};

onMounted(async () => {
  await loadDepartmentOptions();
  await loadPeopleOptions();
  await loadUserOptions();
  await loadLicense();
  await loadFields();
});
</script>



