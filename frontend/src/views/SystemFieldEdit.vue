<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">编辑系统字段</h2>
          <p class="text-sm text-muted-foreground">更新系统资产自定义字段。</p>
        </div>
        <RouterLink :to="`/system-field-categories/${categoryId}/fields`">
          <Button variant="outline">返回字段</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">字段名称 <span class="text-destructive">*</span></label>
          <Input v-model="form.name" placeholder="字段名称" :class="inputErrorClass('name')" data-error-key="name" />
        </div>
        <div class="form-field">
          <label class="form-label">字段键 <span class="text-destructive">*</span></label>
          <Input
            v-model="form.field_key"
            placeholder="字段键"
            :class="inputErrorClass('field_key')"
            data-error-key="field_key"
          />
        </div>
        <div class="form-field">
          <label class="form-label">字段类型 <span class="text-destructive">*</span></label>
          <Select v-model="form.field_type">
            <SelectTrigger class="w-full" :class="inputErrorClass('field_type')" data-error-key="field_type">
              <SelectValue placeholder="字段类型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="text">文本</SelectItem>
              <SelectItem value="textarea">多行文本</SelectItem>
              <SelectItem value="markdown">Markdown 文档</SelectItem>
              <SelectItem value="topology">拓扑图</SelectItem>
              <SelectItem value="number">数字</SelectItem>
              <SelectItem value="date">日期</SelectItem>
              <SelectItem value="single_select">单选</SelectItem>
              <SelectItem value="multi_select">多选</SelectItem>
              <SelectItem value="compound">组合字段</SelectItem>
              <SelectItem value="boolean">布尔</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div v-if="canUseOptions" class="form-field">
          <label class="form-label">数据源 <span class="text-destructive">*</span></label>
          <Select v-model="form.data_source">
            <SelectTrigger class="w-full" :class="inputErrorClass('data_source')" data-error-key="data_source">
              <SelectValue placeholder="选择数据源" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="static">静态选项</SelectItem>
              <SelectItem value="system_assets">系统资产（系统名称）</SelectItem>
              <SelectItem value="departments">部门列表</SelectItem>
              <SelectItem value="people">人员列表</SelectItem>
              <SelectItem value="users">用户列表</SelectItem>
              <SelectItem value="dict">静态数据源</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div v-if="canUseOptions && form.data_source === 'dict'" class="form-field">
          <label class="form-label">数据源类型 <span class="text-destructive">*</span></label>
          <Select v-model="dictTypeCode">
            <SelectTrigger class="w-full" :class="inputErrorClass('dict_type')" data-error-key="dict_type">
              <SelectValue placeholder="选择类型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="item in filteredDictTypes" :key="item.id" :value="item.code">
                {{ item.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div v-if="canUseOptions && form.data_source === 'static'" class="form-field">
          <label class="form-label">选项 <span class="text-destructive">*</span></label>
          <Input
            v-model="options"
            placeholder="选项（单选/多选用逗号分隔）"
            :class="inputErrorClass('options')"
            data-error-key="options"
          />
        </div>
        <div v-if="form.field_type === 'compound'" class="form-field md:col-span-2">
          <label class="form-label">组合子字段 <span class="text-destructive">*</span></label>
          <div class="grid gap-3">
            <div
              v-for="(item, index) in compoundFields"
              :key="index"
              class="rounded-md border p-3"
              :class="inputErrorClass('compound_fields')"
              data-error-key="compound_fields"
            >
              <div class="mb-2 flex items-center justify-between">
                <span class="text-xs text-muted-foreground">子字段 {{ index + 1 }}</span>
                <Button
                  size="sm"
                  variant="outline"
                  type="button"
                  :disabled="compoundFields.length <= 1"
                  @click="removeCompoundField(index)"
                >
                  删除
                </Button>
              </div>
              <div class="grid gap-2 md:grid-cols-3">
                <div class="form-field">
                  <label class="form-label text-xs">名称</label>
                  <Input v-model="item.name" placeholder="例如 端口号" />
                </div>
                <div class="form-field">
                  <label class="form-label text-xs">字段键</label>
                  <Input v-model="item.key" placeholder="例如 port" />
                </div>
                <div class="form-field">
                  <label class="form-label text-xs">类型</label>
                  <Select v-model="item.type">
                    <SelectTrigger class="w-full">
                      <SelectValue placeholder="类型" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="text">文本</SelectItem>
                      <SelectItem value="textarea">多行文本</SelectItem>
                      <SelectItem value="markdown">Markdown</SelectItem>
                      <SelectItem value="number">数字</SelectItem>
                      <SelectItem value="date">日期</SelectItem>
                      <SelectItem value="single_select">单选</SelectItem>
                      <SelectItem value="multi_select">多选</SelectItem>
                      <SelectItem value="boolean">布尔</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div v-if="item.type === 'single_select' || item.type === 'multi_select'" class="form-field mt-2">
                <label class="form-label text-xs">选项</label>
                <Input v-model="item.options" placeholder="使用逗号分隔，如 A,B,C" />
              </div>
            </div>
            <Button size="sm" variant="outline" type="button" @click="addCompoundField">+ 添加子字段</Button>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label">必填</label>
          <div class="flex items-center gap-2 text-sm">
            <Checkbox v-model="form.is_required" />
            <span class="text-muted-foreground">是</span>
          </div>
        </div>
        <div v-if="canRepeat" class="form-field">
          <label class="form-label">可重复</label>
          <div class="flex items-center gap-3 text-sm">
            <Switch v-model="form.repeatable" />
            <span class="text-muted-foreground">启用</span>
          </div>
        </div>
        <div v-if="form.field_type === 'date'" class="form-field">
          <label class="form-label">开启提醒</label>
          <div class="flex items-center gap-3 text-sm">
            <Switch v-model="form.reminder_enabled" />
            <span class="text-muted-foreground">启用</span>
          </div>
        </div>
        <div v-if="form.field_type === 'multi_select'" class="form-field">
          <label class="form-label">多选模式</label>
          <ToggleGroup v-model="form.multi_select_mode" type="single">
            <ToggleGroupItem value="checkbox">列表多选</ToggleGroupItem>
            <ToggleGroupItem value="tags">标签多选</ToggleGroupItem>
          </ToggleGroup>
        </div>
        <div v-if="form.field_type === 'single_select' || form.field_type === 'multi_select'" class="form-field">
          <label class="form-label">启用搜索</label>
          <div class="flex items-center gap-3 text-sm">
            <Switch v-model="form.searchable" />
            <span class="text-muted-foreground">开启后可搜索选项</span>
          </div>
        </div>
        <div v-if="form.field_type === 'date' && form.reminder_enabled" class="form-field">
          <label class="form-label">提前提醒天数</label>
          <Input v-model="form.reminder_days" type="number" placeholder="例如 7" />
        </div>
        <div class="form-field">
          <label class="form-label">排序</label>
          <Input v-model="form.sort_order" type="number" placeholder="排序" />
        </div>
        <div class="form-field">
          <label class="form-label">关联字段</label>
          <Select v-model="rule.depends_on">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择字段（可选）" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem :value="noneValue">无</SelectItem>
              <SelectItem v-for="item in existingFields" :key="item.id" :value="String(item.id)">
                {{ item.name }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field">
          <label class="form-label">关联字段触发值</label>
          <Input v-model="rule.value" placeholder="当字段值等于..." />
        </div>
        <div class="form-field">
          <label class="form-label">本字段动作</label>
          <Select v-model="rule.action">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="显示/隐藏" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="show">满足则显示</SelectItem>
              <SelectItem value="hide">满足则隐藏</SelectItem>
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
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Switch } from "../components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "../components/ui/toggle-group";
import { toast } from "../components/ui/sonner";

const route = useRoute();
const router = useRouter();
const fieldId = Number(route.params.fieldId);
const categoryId = Number(route.params.id);
const options = ref("");
const existingFields = ref([]);
const dictTypes = ref([]);
const dictTypeCode = ref("");
const fieldScope = "system";
const filteredDictTypes = computed(() =>
  dictTypes.value.filter((item) => item.scope === "global" || item.scope === fieldScope)
);
const noneValue = "__none__";
const rule = reactive({ depends_on: noneValue, value: "", action: "show" });
const errors = ref({});
const compoundFields = ref([{ name: "", key: "", type: "text", options: "" }]);
const form = ref({
  name: "",
  field_key: "",
  field_type: "text",
  is_required: false,
  repeatable: false,
  data_source: "static",
  searchable: false,
  multi_select_mode: "checkbox",
  reminder_enabled: false,
  reminder_days: null,
  sort_order: 0
});
const repeatableTypes = ["text", "textarea", "number", "single_select"];
const optionTypes = ["single_select", "multi_select"];
const canRepeat = computed(() => repeatableTypes.includes(form.value.field_type));
const canUseOptions = computed(() => optionTypes.includes(form.value.field_type));
const inputErrorClass = (key) => (errors.value[key] ? "border-destructive" : "");
const scrollToFirstError = () => {
  const errorKey = Object.keys(errors.value).find((key) => errors.value[key]);
  if (!errorKey) return;
  const el = document.querySelector(`[data-error-key="${errorKey}"]`);
  if (el?.scrollIntoView) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
  }
};
const validateRequired = () => {
  errors.value = {};
  const labels = [];
  if (!form.value.name?.trim()) {
    errors.value.name = true;
    labels.push("字段名称");
  }
  if (!form.value.field_key?.trim()) {
    errors.value.field_key = true;
    labels.push("字段键");
  }
  if (!form.value.field_type) {
    errors.value.field_type = true;
    labels.push("字段类型");
  }
  if (canUseOptions.value && !form.value.data_source) {
    errors.value.data_source = true;
    labels.push("数据源");
  }
  if (canUseOptions.value && form.value.data_source === "dict" && !dictTypeCode.value) {
    errors.value.dict_type = true;
    labels.push("数据源类型");
  }
  if (canUseOptions.value && form.value.data_source === "static") {
    const parsed = options.value.split(",").map((item) => item.trim()).filter(Boolean);
    if (!parsed.length) {
      errors.value.options = true;
      labels.push("选项");
    }
  }
  if (form.value.field_type === "compound") {
    const cleaned = compoundFields.value.filter(
      (item) => String(item.name || "").trim() || String(item.key || "").trim()
    );
    const invalid = cleaned.some((item) => {
      const type = String(item.type || "").trim();
      if (!String(item.name || "").trim() || !String(item.key || "").trim() || !type) return true;
      if (type === "single_select" || type === "multi_select") {
        return !String(item.options || "")
          .split(",")
          .map((opt) => opt.trim())
          .filter(Boolean).length;
      }
      return false;
    });
    if (!cleaned.length || invalid) {
      errors.value.compound_fields = true;
      labels.push("组合子字段");
    }
  }
  if (labels.length) {
    scrollToFirstError();
    toast.error(`请填写必填项：${labels.join("、")}`);
    return false;
  }
  return true;
};

const load = async () => {
  const { data } = await api.get(`/system-field-categories/${categoryId}/fields`);
  const { data: tree } = await api.get("/system-field-categories/tree");
  existingFields.value = tree.flatMap((item) => item.fields || []).filter((item) => item.id !== fieldId);
  const current = data.find((item) => item.id === fieldId);
  if (!current) return;
  form.value = {
    name: current.name,
    field_key: current.field_key,
    field_type: current.field_type === "combo_select" ? "single_select" : current.field_type,
    is_required: current.is_required,
    sort_order: current.sort_order || 0,
    reminder_enabled: Boolean(current.reminder_enabled),
    reminder_days: current.reminder_days ?? null,
    repeatable: Boolean(current.repeatable),
    data_source: current.data_source || "static",
    searchable: current.field_type === "combo_select" ? true : Boolean(current.searchable),
    multi_select_mode: current.multi_select_mode || "checkbox"
  };
  if (current.field_type === "compound") {
    compoundFields.value = Array.isArray(current.options) && current.options.length
      ? current.options.map((sub) => ({
          name: sub.name || "",
          key: sub.key || "",
          type: sub.type || "text",
          options: Array.isArray(sub.options) ? sub.options.join(",") : ""
        }))
      : [{ name: "", key: "", type: "text", options: "" }];
  }
  if (current.data_source && current.data_source.startsWith("dict:")) {
    form.value.data_source = "dict";
    dictTypeCode.value = current.data_source.replace("dict:", "");
  }
  options.value =
    Array.isArray(current.options) && current.options.every((opt) => typeof opt === "string")
      ? current.options.join(",")
      : "";
  if (!canRepeat.value) {
    form.value.repeatable = false;
  }
  if (!canUseOptions.value) {
    options.value = "";
  }
  if (form.value.data_source !== "static") {
    options.value = "";
  }
  const currentRule = Array.isArray(current.visibility_rules) ? current.visibility_rules[0] : null;
  if (currentRule) {
    rule.depends_on = currentRule.depends_on ? String(currentRule.depends_on) : noneValue;
    rule.value = currentRule.value ?? "";
    rule.action = currentRule.action || "show";
  }
};

const save = async () => {
  if (!validateRequired()) return;
  const parsedOptions = canUseOptions.value && form.value.data_source === "static"
    ? options.value.split(",").map((item) => item.trim()).filter(Boolean)
    : [];
  const compoundPayload =
    form.value.field_type === "compound"
      ? compoundFields.value
          .filter((item) => String(item.name || "").trim() && String(item.key || "").trim())
          .map((item) => ({
            name: item.name.trim(),
            key: item.key.trim(),
            type: item.type || "text",
            options:
              item.type === "single_select" || item.type === "multi_select"
                ? String(item.options || "")
                    .split(",")
                    .map((opt) => opt.trim())
                    .filter(Boolean)
                : null
          }))
      : null;
  await api.put(`/system-field-categories/fields/${fieldId}`, {
    ...form.value,
    repeatable: canRepeat.value ? form.value.repeatable : false,
    data_source: canUseOptions.value
      ? form.value.data_source === "dict"
        ? `dict:${dictTypeCode.value}`
        : form.value.data_source
      : null,
    searchable: ["single_select", "multi_select"].includes(form.value.field_type) ? Boolean(form.value.searchable) : false,
    multi_select_mode: form.value.field_type === "multi_select" ? form.value.multi_select_mode : null,
    reminder_enabled: form.value.field_type === "date" ? form.value.reminder_enabled : false,
    reminder_days:
      form.value.field_type === "date" && form.value.reminder_enabled ? Number(form.value.reminder_days || 0) : null,
    options:
      form.value.field_type === "compound"
        ? compoundPayload
        : form.value.data_source === "static" && parsedOptions.length
        ? parsedOptions
        : null,
    visibility_rules:
      rule.depends_on !== noneValue && rule.value
        ? [
            {
              depends_on: Number(rule.depends_on),
              operator: "eq",
              value: rule.value,
              action: rule.action
            }
          ]
        : null
  });
  router.push(`/system-field-categories/${categoryId}/fields`);
};

const addCompoundField = () => {
  compoundFields.value = [...compoundFields.value, { name: "", key: "", type: "text", options: "" }];
};

const removeCompoundField = (index) => {
  const next = compoundFields.value.filter((_, i) => i !== index);
  compoundFields.value = next.length ? next : [{ name: "", key: "", type: "text", options: "" }];
};

const loadDictTypes = async () => {
  try {
    const { data } = await api.get("/dictionaries/types");
    dictTypes.value = Array.isArray(data)
      ? data.filter((item) => String(item.code || "").trim() !== "")
      : [];
  } catch {
    dictTypes.value = [];
  }
};

onMounted(() => {
  load();
  loadDictTypes();
});

watch(
  () => form.value.field_type,
  () => {
    if (!canRepeat.value) {
      form.value.repeatable = false;
    }
    if (!canUseOptions.value) {
      options.value = "";
      form.value.data_source = "static";
    }
    if (form.value.field_type !== "multi_select") {
      form.value.multi_select_mode = "checkbox";
    }
    if (!["single_select", "multi_select"].includes(form.value.field_type)) {
      form.value.searchable = false;
    }
    if (form.value.data_source !== "dict") {
      dictTypeCode.value = "";
    }
  }
);

watch(
  () => form.value.data_source,
  () => {
    if (form.value.data_source !== "static") {
      options.value = "";
    }
    if (form.value.data_source !== "dict") {
      dictTypeCode.value = "";
    }
  }
);
</script>



