<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="grid gap-4 md:grid-cols-4 items-end">
        <div class="form-field">
          <label class="form-label">关键词</label>
          <Input v-model="q" placeholder="搜索系统名称/编码" />
        </div>
        <div class="form-field">
          <label class="form-label">系统状态</label>
          <Select v-model="status">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="系统状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="开发中">开发中</SelectItem>
              <SelectItem value="测试中">测试中</SelectItem>
              <SelectItem value="运行中">运行中</SelectItem>
              <SelectItem value="维护中">维护中</SelectItem>
              <SelectItem value="已下线">已下线</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex items-end gap-3 md:col-span-2">
          <Button :disabled="loading" @click="load(true)">查询</Button>
          <RouterLink to="/systems/new">
            <Button variant="outline">新增系统</Button>
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="rounded-lg border bg-background">
      <div v-if="loading" class="flex items-center justify-center gap-2 py-10 text-sm text-muted-foreground">
        <Spinner class="size-5" />
        <span>加载中...</span>
      </div>
      <table v-else class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">系统名称</th>
            <th class="px-4 py-2">系统编码</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2">分类</th>
            <th class="px-4 py-2">技术负责人</th>
            <th class="px-4 py-2">运维负责人</th>
            <th class="px-4 py-2">运维负责人B</th>
            <th class="px-4 py-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in items"
            :key="item.id"
            class="border-b cursor-pointer hover:bg-muted/40"
            @click="openDetail(item.id)"
          >
            <td class="px-4 py-2">{{ item.app_name }}</td>
            <td class="px-4 py-2">{{ item.app_code }}</td>
            <td class="px-4 py-2">{{ formatBaseFieldValue("app_status", item.app_status) }}</td>
            <td class="px-4 py-2">{{ formatBaseFieldValue("app_category", item.app_category) }}</td>
            <td class="px-4 py-2">{{ item.tech_owner }}</td>
            <td class="px-4 py-2">{{ item.ops_owner_name || item.ops_owner }}</td>
            <td class="px-4 py-2">{{ item.ops_owner_b_name || item.ops_owner_b }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2" @click.stop>
                <RouterLink :to="`/systems/${item.id}/edit`" @click.stop>
                  <Button size="sm" variant="outline" @click.stop>编辑</Button>
                </RouterLink>
                <Button size="sm" variant="destructive" @click.stop="askDelete(item.id)">删除</Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="flex flex-col gap-3 border-t px-4 py-3 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
        <div>
          共 {{ total }} 条，当前第 {{ page }} / {{ totalPages }} 页
        </div>
        <div class="flex items-center gap-2">
          <span>每页</span>
          <Select v-model="sizeText" @update:modelValue="onSizeChange">
            <SelectTrigger class="h-8 w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
          <Button size="sm" variant="outline" :disabled="loading || page <= 1" @click="goPrevPage">上一页</Button>
          <Button size="sm" variant="outline" :disabled="loading || page >= totalPages" @click="goNextPage">下一页</Button>
        </div>
      </div>
    </div>

    <AlertDialog v-model:open="confirmOpen">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>确认删除</AlertDialogTitle>
          <AlertDialogDescription>删除后将无法恢复。</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>取消</AlertDialogCancel>
          <AlertDialogAction @click="confirmDelete">删除</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>

    <Drawer v-model:open="detailOpen">
      <DrawerContent class="w-full overflow-auto">
        <DrawerHeader>
          <DrawerTitle>系统资产详情</DrawerTitle>
          <DrawerDescription>查看系统基础信息与自定义字段。</DrawerDescription>
        </DrawerHeader>
        <div class="space-y-6 px-6 pb-8">
          <div v-for="category in visibleCategories" :key="category.id" class="space-y-3">
            <div class="text-sm font-semibold">{{ category.name }}</div>
            <div class="rounded-lg border bg-background">
              <div class="grid gap-2 p-4 md:grid-cols-3">
                <div v-for="field in category.fields" :key="field.id" class="flex items-start gap-3">
                  <div class="w-24 text-sm font-medium">{{ field.name }}</div>
                  <div v-if="field.field_type === 'markdown'" class="space-y-1">
                    <Button
                      size="sm"
                      variant="outline"
                      type="button"
                      :disabled="!hasMarkdownValue(resolveFieldValue(field))"
                      @click="openMarkdownPreview(field, resolveFieldValue(field))"
                    >
                      查看文档
                    </Button>
                    <div class="text-xs text-muted-foreground">
                      {{ markdownSummary(resolveFieldValue(field)) }}
                    </div>
                  </div>
                  <div
                    v-else-if="field.field_type === 'compound' && getCompoundMarkdownEntries(field, resolveFieldValue(field)).length"
                    class="space-y-1"
                  >
                    <div class="flex flex-wrap gap-1">
                      <Button
                        v-for="entry in getCompoundMarkdownEntries(field, resolveFieldValue(field))"
                        :key="entry.key"
                        size="sm"
                        variant="outline"
                        type="button"
                        @click="openCompoundMarkdownPreview(field, entry)"
                      >
                        {{ entry.label }}
                      </Button>
                    </div>
                    <div class="text-xs text-muted-foreground">
                      {{ `共 ${getCompoundMarkdownEntries(field, resolveFieldValue(field)).length} 篇文档` }}
                    </div>
                  </div>
                  <div v-else-if="field.field_type === 'topology'" class="space-y-1">
                    <Button
                      size="sm"
                      variant="outline"
                      type="button"
                      :disabled="!hasTopologyValue(resolveFieldValue(field))"
                      @click="openTopologyPreview(field, resolveFieldValue(field))"
                    >
                      查看拓扑
                    </Button>
                    <div class="text-xs text-muted-foreground">
                      {{ topologySummary(resolveFieldValue(field)) }}
                    </div>
                  </div>
                  <div v-else class="text-sm text-muted-foreground">
                    {{ formatFieldValue(field, resolveFieldValue(field)) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DrawerContent>
    </Drawer>

    <Dialog v-model:open="markdownPreviewOpen">
      <DialogContent class="w-[98vw] max-w-[min(98vw,1400px)] sm:max-w-[min(98vw,1400px)] md:max-w-[min(98vw,1400px)]">
        <DialogHeader>
          <DialogTitle>{{ markdownPreviewTitle || "Markdown 文档" }}</DialogTitle>
          <DialogDescription>只读预览</DialogDescription>
        </DialogHeader>
        <div class="max-h-[70vh] overflow-auto rounded-md border p-4">
          <MdPreview editorId="system-asset-markdown-preview" :modelValue="markdownPreviewContent" language="zh-CN" />
        </div>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="topologyPreviewOpen">
      <DialogContent class="w-[98vw] max-w-[min(98vw,1500px)] sm:max-w-[min(98vw,1500px)] md:max-w-[min(98vw,1500px)]">
        <DialogHeader>
          <DialogTitle>{{ topologyPreviewTitle || "拓扑图" }}</DialogTitle>
          <DialogDescription>只读预览</DialogDescription>
        </DialogHeader>
        <TopologyCanvas :model-value="topologyPreviewContent" :readonly="true" />
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from "../components/ui/drawer";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "../components/ui/dialog";
import { Spinner } from "../components/ui/spinner";
import TopologyCanvas from "../components/topology/TopologyCanvas.vue";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter
} from "../components/ui/alert-dialog";

const MdPreview = defineAsyncComponent(async () => {
  await import("md-editor-v3/lib/style.css");
  const mod = await import("md-editor-v3");
  return mod.MdPreview;
});

const items = ref([]);
const q = ref("");
const status = ref("all");
const loading = ref(false);
const page = ref(1);
const size = ref(20);
const sizeText = ref("20");
const total = ref(0);
const confirmOpen = ref(false);
const pendingId = ref(null);
const detailOpen = ref(false);
const detail = ref(null);
const detailCategories = ref([]);
const detailValues = ref({});
const markdownPreviewOpen = ref(false);
const markdownPreviewTitle = ref("");
const markdownPreviewContent = ref("");
const topologyPreviewOpen = ref(false);
const topologyPreviewTitle = ref("");
const topologyPreviewContent = ref("");
const optionSourceCache = ref({});
const fieldOptionLabelMap = ref({});
const baseFieldMap = ref({});
const totalPages = computed(() => {
  const currentSize = Number(size.value) || 20;
  const pages = Math.ceil((Number(total.value) || 0) / currentSize);
  return Math.max(1, pages);
});

const baseFieldKeys = new Set([
  "app_name",
  "app_code",
  "app_status",
  "biz_owner",
  "tech_owner",
  "ops_owner",
  "ops_owner_b"
]);

const load = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1;
  }
  loading.value = true;
  try {
    const { data } = await api.get("/systems", {
      params: {
        page: page.value,
        size: size.value,
        q: q.value || null,
        app_status: status.value === "all" ? null : status.value
      }
    });
    items.value = Array.isArray(data.items) ? data.items : [];
    total.value = Number(data.total || 0);
    const pages = Math.max(1, Math.ceil(total.value / size.value));
    if (page.value > pages) {
      page.value = pages;
    }
  } finally {
    loading.value = false;
  }
};

const onSizeChange = (value) => {
  const next = Number(value);
  if (!next || Number.isNaN(next)) return;
  size.value = next;
  sizeText.value = String(next);
  load(true);
};

const goPrevPage = () => {
  if (page.value <= 1) return;
  page.value -= 1;
  load();
};

const goNextPage = () => {
  if (page.value >= totalPages.value) return;
  page.value += 1;
  load();
};

const askDelete = (id) => {
  pendingId.value = id;
  confirmOpen.value = true;
};

const confirmDelete = async () => {
  if (!pendingId.value) return;
  await api.delete(`/systems/${pendingId.value}`);
  confirmOpen.value = false;
  pendingId.value = null;
  await load();
};

const safeJsonParse = (value) => {
  if (typeof value !== "string") return value;
  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
};

const normalizeOptionPairs = (options) => {
  if (!Array.isArray(options)) return [];
  return options
    .map((item) => {
      if (item && typeof item === "object") {
        const rawValue = item.value ?? item.label ?? item.name ?? "";
        const rawLabel = item.label ?? item.name ?? item.value ?? "";
        return {
          value: String(rawValue ?? "").trim(),
          label: String(rawLabel ?? "").trim()
        };
      }
      const text = String(item ?? "").trim();
      return { value: text, label: text };
    })
    .filter((item) => item.value);
};

const getOptionsFromField = (field) => {
  const source = String(field?.data_source || "");
  if (source === "users" && optionSourceCache.value.users) return optionSourceCache.value.users;
  if (source === "departments" && optionSourceCache.value.departments) return optionSourceCache.value.departments;
  if (source === "people" && optionSourceCache.value.people) return optionSourceCache.value.people;
  if (source === "system_assets" && optionSourceCache.value.system_assets) return optionSourceCache.value.system_assets;
  if (source.startsWith("dict:")) {
    const code = source.replace("dict:", "");
    if (code && optionSourceCache.value[`dict:${code}`]) return optionSourceCache.value[`dict:${code}`];
  }
  return normalizeOptionPairs(field?.options);
};

const buildOptionLabelMap = (field) => {
  const pairs = getOptionsFromField(field);
  const map = new Map();
  pairs.forEach((item) => {
    if (!item.value) return;
    map.set(item.value, item.label || item.value);
  });
  return map;
};

const formatSingleWithField = (field, rawValue) => {
  const key = String(rawValue ?? "").trim();
  if (!key) return "-";
  const labelMap = fieldOptionLabelMap.value[field.id];
  return labelMap?.get(key) || key;
};

const formatMultiWithField = (field, value) => {
  const list = Array.isArray(value) ? value : [value];
  const labelMap = fieldOptionLabelMap.value[field.id];
  return list
    .map((item) => {
      const key = String(item ?? "").trim();
      if (!key) return "";
      return labelMap?.get(key) || key;
    })
    .filter(Boolean)
    .join("，");
};

const formatCompoundWithField = (field, rows) => {
  const subFields = Array.isArray(field?.options) ? field.options : [];
  if (!Array.isArray(rows) || !rows.length || !subFields.length) return "-";
  const formatted = rows
    .map((row) =>
      subFields
        .map((sub) => {
          const subValue = row?.[sub.key];
          if (subValue === null || subValue === undefined || subValue === "") return null;
          if (sub.type === "single_select" || sub.type === "combo_select") {
            const subMap = new Map(normalizeOptionPairs(sub.options).map((item) => [item.value, item.label || item.value]));
            return `${sub.name}:${subMap.get(String(subValue)) || subValue}`;
          }
          if (sub.type === "multi_select") {
            const subMap = new Map(normalizeOptionPairs(sub.options).map((item) => [item.value, item.label || item.value]));
            const subList = Array.isArray(subValue) ? subValue : [subValue];
            const text = subList
              .map((item) => {
                const key = String(item ?? "").trim();
                return key ? (subMap.get(key) || key) : "";
              })
              .filter(Boolean)
              .join("，");
            return text ? `${sub.name}:${text}` : null;
          }
          return `${sub.name}:${subValue}`;
        })
        .filter(Boolean)
        .join("，")
    )
    .filter(Boolean)
    .join("；");
  return formatted || "-";
};

const preloadOptionSources = async (fields) => {
  const sources = new Set();
  (fields || []).forEach((field) => {
    const source = String(field?.data_source || "");
    if (source && source !== "static") sources.add(source);
  });
  const tasks = [];
  if (sources.has("users") && !optionSourceCache.value.users) {
    tasks.push(
      api.get("/users/options").then(({ data }) => {
        optionSourceCache.value.users = normalizeOptionPairs(
          (Array.isArray(data) ? data : []).map((item) => ({ value: item.value, label: item.label }))
        );
      })
    );
  }
  if (sources.has("departments") && !optionSourceCache.value.departments) {
    tasks.push(
      api.get("/departments/options").then(({ data }) => {
        optionSourceCache.value.departments = normalizeOptionPairs(
          (Array.isArray(data) ? data : []).map((item) => ({ value: item.value, label: item.label }))
        );
      })
    );
  }
  if (sources.has("people") && !optionSourceCache.value.people) {
    tasks.push(
      api.get("/people/options").then(({ data }) => {
        optionSourceCache.value.people = normalizeOptionPairs(
          (Array.isArray(data) ? data : []).map((item) => ({ value: item.value, label: item.label }))
        );
      })
    );
  }
  if (sources.has("system_assets") && !optionSourceCache.value.system_assets) {
    tasks.push(
      api.get("/systems/options").then(({ data }) => {
        optionSourceCache.value.system_assets = normalizeOptionPairs(
          (Array.isArray(data) ? data : []).map((item) => ({ value: item.value, label: item.label }))
        );
      })
    );
  }
  Array.from(sources)
    .filter((source) => source.startsWith("dict:"))
    .forEach((source) => {
      if (optionSourceCache.value[source]) return;
      const code = source.replace("dict:", "");
      if (!code) return;
      tasks.push(
        api.get("/dictionaries/items", { params: { type: code } }).then(({ data }) => {
          optionSourceCache.value[source] = normalizeOptionPairs(
            (Array.isArray(data) ? data : [])
              .filter((item) => item?.is_active !== false)
              .map((item) => ({ value: item.value || item.name, label: item.name }))
          );
        })
      );
    });
  await Promise.all(tasks);
};

const buildFieldOptionMaps = (fields) => {
  const map = {};
  const baseMap = {};
  (fields || []).forEach((field) => {
    const labelMap = buildOptionLabelMap(field);
    map[field.id] = labelMap;
    if (field?.field_key) {
      baseMap[field.field_key] = field;
    }
  });
  fieldOptionLabelMap.value = map;
  baseFieldMap.value = baseMap;
};

const formatBaseFieldValue = (fieldKey, rawValue) => {
  const key = String(rawValue ?? "").trim();
  if (!key) return "-";
  const field = baseFieldMap.value[fieldKey];
  const labelMap = field ? fieldOptionLabelMap.value[field.id] : null;
  return labelMap?.get(key) || key;
};

const formatFieldValue = (field, rawValue) => {
  const value = safeJsonParse(rawValue);
  if (value === null || value === undefined || value === "") return "-";
  if (field?.field_type === "compound") {
    return formatCompoundWithField(field, value);
  }
  if (field?.field_type === "single_select" || field?.field_type === "combo_select") {
    return formatSingleWithField(field, value);
  }
  if (field?.field_type === "multi_select") {
    return formatMultiWithField(field, value);
  }
  if (Array.isArray(value)) return value.join("，");
  return value;
};

const getCompoundMarkdownEntries = (field, rawValue) => {
  if (field?.field_type !== "compound") return [];
  const value = safeJsonParse(rawValue);
  const rows = Array.isArray(value) ? value : [];
  const markdownSubs = (Array.isArray(field?.options) ? field.options : []).filter((sub) => sub.type === "markdown");
  if (!rows.length || !markdownSubs.length) return [];
  const entries = [];
  rows.forEach((row, rowIndex) => {
    markdownSubs.forEach((sub) => {
      const content = String(row?.[sub.key] || "").trim();
      if (!content) return;
      entries.push({
        key: `${rowIndex}-${sub.key}`,
        label: `第${rowIndex + 1}行·${sub.name || sub.key}`,
        content
      });
    });
  });
  return entries;
};

const hasMarkdownValue = (rawValue) => {
  const value = safeJsonParse(rawValue);
  return value !== null && value !== undefined && String(value).trim() !== "";
};

const markdownSummary = (rawValue) => {
  if (!hasMarkdownValue(rawValue)) return "未填写";
  const value = String(safeJsonParse(rawValue));
  return `已填写，${value.length} 字符`;
};

const openMarkdownPreview = (field, rawValue) => {
  if (!hasMarkdownValue(rawValue)) return;
  markdownPreviewTitle.value = field?.name || "Markdown 文档";
  markdownPreviewContent.value = String(safeJsonParse(rawValue) || "");
  markdownPreviewOpen.value = true;
};

const openCompoundMarkdownPreview = (field, entry) => {
  markdownPreviewTitle.value = `${field?.name || "组合字段"} / ${entry.label}`;
  markdownPreviewContent.value = entry.content || "";
  markdownPreviewOpen.value = true;
};

const hasTopologyValue = (rawValue) => {
  if (!rawValue) return false;
  try {
    const parsed = typeof rawValue === "string" ? JSON.parse(rawValue) : rawValue;
    return Array.isArray(parsed?.nodes) && parsed.nodes.length > 0;
  } catch {
    return false;
  }
};

const topologySummary = (rawValue) => {
  if (!rawValue) return "未绘制";
  try {
    const parsed = typeof rawValue === "string" ? JSON.parse(rawValue) : rawValue;
    const nodes = Array.isArray(parsed?.nodes) ? parsed.nodes.length : 0;
    const edges = Array.isArray(parsed?.edges) ? parsed.edges.length : 0;
    return nodes > 0 ? `节点 ${nodes} / 连线 ${edges}` : "未绘制";
  } catch {
    return "已填写";
  }
};

const openTopologyPreview = (field, rawValue) => {
  if (!rawValue) return;
  topologyPreviewTitle.value = field?.name || "拓扑图";
  topologyPreviewContent.value = String(rawValue || "");
  topologyPreviewOpen.value = true;
};

const resolveFieldValue = (field) => {
  if (baseFieldKeys.has(field.field_key)) {
    if (field.field_key === "ops_owner") {
      return detail.value?.ops_owner_name || detail.value?.ops_owner;
    }
    if (field.field_key === "ops_owner_b") {
      return detail.value?.ops_owner_b_name || detail.value?.ops_owner_b;
    }
    return detail.value?.[field.field_key];
  }
  return detailValues.value[field.id];
};

const openDetail = async (id) => {
  detailOpen.value = true;
  detail.value = null;
  detailCategories.value = [];
  detailValues.value = {};
  const [detailRes, categoriesRes, valuesRes] = await Promise.all([
    api.get(`/systems/${id}`),
    api.get("/system-field-categories/tree"),
    api.get(`/systems/${id}/fields`)
  ]);
  detail.value = detailRes.data;
  detailCategories.value = categoriesRes.data;
  const allFields = detailCategories.value.flatMap((category) => Array.isArray(category.fields) ? category.fields : []);
  await preloadOptionSources(allFields);
  buildFieldOptionMaps(allFields);
  const map = {};
  for (const item of valuesRes.data) {
    map[item.field_id] = item.value;
  }
  detailValues.value = map;
};

const visibleCategories = computed(() =>
  detailCategories.value.filter((category) => Array.isArray(category.fields) && category.fields.length > 0)
);

onMounted(async () => {
  const { data } = await api.get("/system-field-categories/tree");
  const allFields = (Array.isArray(data) ? data : []).flatMap((category) => Array.isArray(category.fields) ? category.fields : []);
  await preloadOptionSources(allFields);
  buildFieldOptionMaps(allFields);
  await load();
});
</script>



