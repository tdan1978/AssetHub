<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增资产</h2>
          <p class="text-sm text-muted-foreground">填写基础信息与自定义字段。</p>
        </div>
        <div class="flex gap-2">
          <RouterLink :to="backLink">
            <Button variant="outline">返回列表</Button>
          </RouterLink>
          <Button @click="save">保存</Button>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-4 form-grid-divider-md-4">
        <div class="form-field">
          <label class="form-label">SN</label>
          <Input v-model="form.sn" placeholder="SN" :class="inputErrorClass('sn')" :data-error-key="'sn'" />
        </div>
        <div class="form-field">
          <label class="form-label">编号</label>
          <Input v-model="form.asset_no" placeholder="自动生成" disabled />
        </div>
        <div class="form-field">
          <label class="form-label">名称</label>
          <Input v-model="form.name" placeholder="名称" :class="inputErrorClass('name')" :data-error-key="'name'" />
        </div>
        <div class="form-field">
          <label class="form-label">资产类型</label>
          <Select v-model="form.category_id" @update:modelValue="onCategoryChange">
            <SelectTrigger class="w-full" :class="inputErrorClass('category_id')" :data-error-key="'category_id'">
              <SelectValue placeholder="选择类型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="item in categories" :key="item.id" :value="item.id">
                {{ item.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div v-show="fields.length" class="mt-6 form-grid-2 xl:grid-cols-3 form-grid-divider-md-2-xl-3">
        <div
          v-for="field in fields"
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
          <div
            v-if="isRepeatableField(field)"
            class="grid gap-2"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          >
            <div v-for="(item, index) in fieldValues[field.id]" :key="index" class="flex items-start gap-2">
              <Input
                v-if="field.field_type === 'text'"
                v-model="fieldValues[field.id][index]"
                :class="['flex-1', inputErrorClass(fieldErrorKey(field))]"
                :data-error-key="fieldErrorKey(field)"
              />
              <Textarea
                v-else-if="field.field_type === 'textarea'"
                v-model="fieldValues[field.id][index]"
                :class="['flex-1', inputErrorClass(fieldErrorKey(field))]"
                :data-error-key="fieldErrorKey(field)"
              />
              <Input
                v-else-if="field.field_type === 'number'"
                v-model="fieldValues[field.id][index]"
                type="number"
                :class="['flex-1', inputErrorClass(fieldErrorKey(field))]"
                :data-error-key="fieldErrorKey(field)"
              />
              <Combobox
                v-else-if="field.field_type === 'combo_select'"
                v-model="fieldValues[field.id][index]"
                :options="getFieldOptions(field)"
                placeholder="选择"
                :class="inputErrorClass(fieldErrorKey(field))"
                :data-error-key="fieldErrorKey(field)"
              />
              <Select v-else-if="field.field_type === 'single_select'" v-model="fieldValues[field.id][index]">
                <SelectTrigger
                  class="w-full"
                  :class="inputErrorClass(fieldErrorKey(field))"
                  :data-error-key="fieldErrorKey(field)"
                >
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
              <Button
                size="sm"
                variant="outline"
                type="button"
                :disabled="fieldValues[field.id].length <= 1"
                @click="removeRepeatableItem(field.id, index)"
              >
                删除
              </Button>
            </div>
            <Button size="sm" variant="outline" type="button" @click="addRepeatableItem(field.id)">+ 添加一项</Button>
          </div>
          <Input
            v-else-if="field.field_type === 'text'"
            v-model="fieldValues[field.id]"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          />
          <Textarea
            v-else-if="field.field_type === 'textarea'"
            v-model="fieldValues[field.id]"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          />
          <Input
            v-else-if="field.field_type === 'number'"
            v-model="fieldValues[field.id]"
            type="number"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          />
          <DatePicker
            v-else-if="field.field_type === 'date'"
            v-model="fieldValues[field.id]"
            :showMonthYearSelect="true"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          />
          <Combobox
            v-else-if="field.field_type === 'combo_select'"
            v-model="fieldValues[field.id]"
            :options="getFieldOptions(field)"
            placeholder="选择"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          />
          <Select v-else-if="field.field_type === 'single_select'" v-model="fieldValues[field.id]">
            <SelectTrigger
              class="w-full"
              :class="inputErrorClass(fieldErrorKey(field))"
              :data-error-key="fieldErrorKey(field)"
            >
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
          <div
            v-else-if="field.field_type === 'compound'"
            class="rounded-md border p-3 space-y-3"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          >
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
          <div
            v-else-if="field.field_type === 'multi_select' && field.multi_select_mode === 'tags'"
            class="space-y-2"
            :class="inputErrorClass(fieldErrorKey(field))"
            :data-error-key="fieldErrorKey(field)"
          >
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
            <SelectTrigger
              class="w-full"
              :class="inputErrorClass(fieldErrorKey(field))"
              :data-error-key="fieldErrorKey(field)"
            >
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
            <Switch v-model="fieldValues[field.id]" />
            <span class="text-muted-foreground">是否</span>
          </div>
        </div>
      </div>

      <div class="mt-4">
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
import { toast } from "../components/ui/sonner";
const MdEditor = defineAsyncComponent(async () => {
  await import("md-editor-v3/lib/style.css");
  const mod = await import("md-editor-v3");
  return mod.MdEditor;
});

const router = useRouter();
const route = useRoute();
const categories = ref([]);
const fields = ref([]);
const fieldValues = ref({});
const repeatableTypes = ["text", "textarea", "number", "single_select", "combo_select"];
const departmentOptions = ref([]);
const peopleOptions = ref([]);
const userOptions = ref([]);
const dictOptions = ref({});
const fieldOptionKeyword = ref({});
const errors = ref({});
const compoundMarkdownEditorOpen = ref(false);
const compoundMarkdownDraft = ref("");
const currentCompoundMarkdownContext = ref(null);
const form = ref({
  sn: "",
  asset_no: "",
  name: "",
  category: "",
  category_id: null,
  status: 0
});
const scopeOptions = ["办公和业务", "数据中心"];
const scope = ref("");
const backLink = computed(() => {
  if (scope.value === "数据中心") return "/assets/datacenter";
  return "/assets/office";
});
const compoundMarkdownEditorTitle = computed(() => {
  const ctx = currentCompoundMarkdownContext.value;
  if (!ctx) return "Markdown 文档";
  return `${ctx.fieldName} / 第${ctx.rowIndex + 1}行 / ${ctx.subName}`;
});

const loadCategories = async () => {
  const dept = scope.value || null;
  const { data } = await api.get("/categories/by-scope", { params: { dept } });
  categories.value = data;
};

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

const onCategoryChange = async () => {
  fields.value = [];
  fieldValues.value = {};
  const categoryId = Number(form.value.category_id);
  form.value.category_id = Number.isNaN(categoryId) ? null : categoryId;
  const categoryItem = categories.value.find((item) => item.id === form.value.category_id);
  form.value.category = categoryItem?.name || "";
  if (!form.value.category_id) return;
  const scopeMap = { office: "办公和业务", datacenter: "数据中心" };
  const dept = categoryItem?.usage_scope ? scopeMap[categoryItem.usage_scope] : null;
  const { data } = await api.get(`/categories/${form.value.category_id}/fields`, {
    params: { dept }
  });
  fields.value = data;
  await preloadDictOptions(fields.value);
  for (const field of fields.value) {
    fieldValues.value[field.id] = initFieldValue(field);
  }
};

const isRepeatableField = (field) => field.repeatable && repeatableTypes.includes(field.field_type);

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

const initFieldValue = (field) => {
  if (field.field_type === "compound") return [initCompoundRow(field)];
  if (isRepeatableField(field)) return [""];
  if (field.field_type === "multi_select") return [];
  if (field.field_type === "boolean") return false;
  return "";
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

const addRepeatableItem = (fieldId) => {
  const current = Array.isArray(fieldValues.value[fieldId]) ? fieldValues.value[fieldId] : [];
  fieldValues.value[fieldId] = [...current, ""];
};

const removeRepeatableItem = (fieldId, index) => {
  const current = Array.isArray(fieldValues.value[fieldId]) ? fieldValues.value[fieldId] : [];
  const next = current.filter((_, i) => i !== index);
  fieldValues.value[fieldId] = next.length ? next : [""];
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

const fieldErrorKey = (field) => `field_${field.id}`;
const inputErrorClass = (key) => (errors.value[key] ? "border-destructive" : "");

const scrollToFirstError = () => {
  const keys = Object.keys(errors.value || {});
  if (!keys.length) return;
  const selector = `[data-error-key="${keys[0]}"]`;
  const el = document.querySelector(selector);
  if (el?.scrollIntoView) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
  }
};

const isEmptyValue = (value) => {
  if (value === null || value === undefined) return true;
  if (Array.isArray(value)) return value.length === 0 || value.every((item) => String(item ?? "").trim() === "");
  if (typeof value === "string") return value.trim() === "";
  return false;
};

const validateRequired = () => {
  const errorLabels = [];
  errors.value = {};
  if (!String(form.value.sn || "").trim()) {
    errors.value.sn = true;
    errorLabels.push("SN");
  }
  if (!String(form.value.name || "").trim()) {
    errors.value.name = true;
    errorLabels.push("名称");
  }
  if (!form.value.category_id) {
    errors.value.category_id = true;
    errorLabels.push("资产类型");
  }

  const visibleFields = fields.value.filter((field) => shouldShowField(field));
  for (const field of visibleFields) {
    if (!field.is_required) continue;
    const value = fieldValues.value[field.id];
    if (isRepeatableField(field)) {
      const list = Array.isArray(value) ? value : [];
      const hasValue = list.some((item) => String(item ?? "").trim() !== "");
      if (!hasValue) {
        errors.value[fieldErrorKey(field)] = true;
        errorLabels.push(field.name);
      }
    } else if (field.field_type === "compound") {
      const rows = Array.isArray(value) ? value : [];
      const subFields = getCompoundFields(field);
      const hasCompleteRow = rows.some((row) =>
        subFields.every((sub) => !isEmptyValue(row?.[sub.key]))
      );
      const hasPartialRow = rows.some((row) => {
        const filled = subFields.filter((sub) => !isEmptyValue(row?.[sub.key])).length;
        return filled > 0 && filled < subFields.length;
      });
      if (!hasCompleteRow || hasPartialRow) {
        errors.value[fieldErrorKey(field)] = true;
        errorLabels.push(field.name);
      }
    } else if (field.field_type === "multi_select") {
      if (!Array.isArray(value) || value.length === 0) {
        errors.value[fieldErrorKey(field)] = true;
        errorLabels.push(field.name);
      }
    } else if (field.field_type !== "boolean") {
      if (isEmptyValue(value)) {
        errors.value[fieldErrorKey(field)] = true;
        errorLabels.push(field.name);
      }
    }
  }

  if (errorLabels.length) {
    toast.error(`请填写必填项：${errorLabels.join("、")}`);
    scrollToFirstError();
    return false;
  }
  return true;
};

const save = async () => {
  if (!validateRequired()) return;
  const { data } = await api.post("/assets", form.value);
  if (fields.value.length) {
    const payload = fields.value.map((field) => ({
      field_id: field.id,
      value: fieldValues.value[field.id]
    }));
    await api.put(`/assets/${data.id}/fields`, payload);
  }
  const categoryItem = categories.value.find((item) => item.id === form.value.category_id);
  const target =
    categoryItem?.usage_scope === "office"
      ? "/assets/office"
      : categoryItem?.usage_scope === "datacenter"
      ? "/assets/datacenter"
      : "/assets";
  router.push(target);
};

onMounted(() => {
  const dept = String(route.query.dept || "");
  if (scopeOptions.includes(dept)) {
    scope.value = dept;
  } else {
    const storedDept = localStorage.getItem("assetDeptScope") || "";
    if (scopeOptions.includes(storedDept)) {
      scope.value = storedDept;
    }
  }
  loadCategories();
  loadDepartmentOptions();
  loadPeopleOptions();
  loadUserOptions();
});
</script>



