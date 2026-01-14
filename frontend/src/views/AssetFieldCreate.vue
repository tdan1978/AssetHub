<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增字段</h2>
          <p class="text-sm text-muted-foreground">为类型添加自定义字段。</p>
        </div>
        <RouterLink :to="`/asset-types/${categoryId}/fields`">
          <Button variant="outline">返回字段</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">字段名称</label>
          <Input v-model="form.name" placeholder="字段名称" />
        </div>
        <div class="form-field">
          <label class="form-label">字段键</label>
          <Input v-model="form.field_key" placeholder="字段键" />
        </div>
        <div class="form-field">
          <label class="form-label">字段类型</label>
          <Select v-model="form.field_type">
            <SelectTrigger class="w-full">
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
        </div>
        <div class="form-field">
          <label class="form-label">选项</label>
          <Input v-model="options" placeholder="选项（单选/多选用逗号分隔）" />
        </div>
        <div class="form-field">
          <label class="form-label">必填</label>
          <div class="flex items-center gap-2 text-sm">
            <Checkbox v-model="form.is_required" />
            <span class="text-muted-foreground">是</span>
          </div>
        </div>
        <div v-if="form.field_type === 'date'" class="form-field">
          <label class="form-label">开启提醒</label>
          <div class="flex items-center gap-3 text-sm">
            <Switch v-model="form.reminder_enabled" />
            <span class="text-muted-foreground">启用</span>
          </div>
        </div>
        <div v-if="form.field_type === 'date' && form.reminder_enabled" class="form-field">
          <label class="form-label">提前提醒天数</label>
          <Input v-model="form.reminder_days" type="number" placeholder="例如 7" />
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
          <label class="form-label">触发值</label>
          <Input v-model="rule.value" placeholder="当字段值等于..." />
        </div>
        <div class="form-field">
          <label class="form-label">动作</label>
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
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Checkbox } from "../components/ui/checkbox";
import { Switch } from "../components/ui/switch";

const route = useRoute();
const router = useRouter();
const categoryId = Number(route.params.id);
const options = ref("");
const existingFields = ref([]);
const noneValue = "__none__";
const rule = reactive({ depends_on: noneValue, value: "", action: "show" });
const form = ref({
  name: "",
  field_key: "",
  field_type: "text",
  is_required: false,
  reminder_enabled: false,
  reminder_days: null,
  sort_order: 0
});

const save = async () => {
  if (!form.value.name || !form.value.field_key) return;
  await api.post(`/categories/${categoryId}/fields`, {
    ...form.value,
    reminder_enabled: form.value.field_type === "date" ? form.value.reminder_enabled : false,
    reminder_days:
      form.value.field_type === "date" && form.value.reminder_enabled ? Number(form.value.reminder_days || 0) : null,
    options: options.value ? options.value.split(",").map((item) => item.trim()).filter(Boolean) : null,
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
  router.push(`/asset-types/${categoryId}/fields`);
};

const loadFields = async () => {
  const { data } = await api.get(`/categories/${categoryId}/fields`);
  existingFields.value = data;
};

onMounted(loadFields);
</script>
