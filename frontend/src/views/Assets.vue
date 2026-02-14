<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="grid gap-4 md:grid-cols-4 items-end">
        <div class="form-field">
          <label class="form-label">关键词</label>
          <Input v-model="q" placeholder="搜索 SN/名称/编号" />
        </div>
        <div class="form-field">
          <label class="form-label">状态</label>
          <Select v-model="status">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="状态" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部</SelectItem>
              <SelectItem value="0">闲置</SelectItem>
              <SelectItem value="1">在用</SelectItem>
              <SelectItem value="2">维修</SelectItem>
              <SelectItem value="3">待报废</SelectItem>
              <SelectItem value="4">已报废</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="flex items-end gap-3 md:col-span-2">
          <Button :disabled="loading" @click="load(true)">查询</Button>
          <RouterLink :to="createLink">
            <Button variant="outline">新增资产</Button>
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
            <th class="px-4 py-2">编号</th>
            <th class="px-4 py-2">SN</th>
            <th class="px-4 py-2">名称</th>
            <th class="px-4 py-2">分类</th>
            <th class="px-4 py-2">状态</th>
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
            <td class="px-4 py-2">{{ item.asset_no }}</td>
            <td class="px-4 py-2">{{ item.sn }}</td>
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2">{{ item.category }}</td>
            <td class="px-4 py-2">{{ statusLabels[item.status] || "-" }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2" @click.stop>
                <DropdownMenu>
                  <DropdownMenuTrigger as-child>
                    <Button size="sm" variant="default">操作</Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" class="w-40">
                    <DropdownMenuItem :disabled="item.status !== 0" @click="openAction('checkout', item)">
                      {{ checkoutLabel }}
                    </DropdownMenuItem>
                    <DropdownMenuItem :disabled="item.status !== 1" @click="openAction('checkin', item)">
                      {{ checkinLabel }}
                    </DropdownMenuItem>
                    <DropdownMenuItem :disabled="![0, 2].includes(item.status)" @click="openAction('discard', item)">
                      报废
                    </DropdownMenuItem>
                    <DropdownMenuItem :disabled="![3, 4].includes(item.status)" @click="openAction('unscrap', item)">
                      取消报废
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <RouterLink :to="`/assets/${item.id}/edit`" @click.stop>
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

    <Dialog v-model:open="actionOpen">
      <DialogContent class="sm:max-w-[420px]">
        <DialogHeader>
          <DialogTitle>{{ actionTitle }}</DialogTitle>
          <DialogDescription>资产：{{ currentAsset?.name || currentAsset?.sn || "-" }}</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div v-if="actionType === 'checkout'" class="space-y-4">
            <div v-if="isDatacenter" class="space-y-4">
              <div class="space-y-2">
                <label class="form-label">数据中心/机房</label>
                <Select v-model="datacenterForm.dc_room">
                  <SelectTrigger class="w-full">
                    <SelectValue placeholder="选择机房" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      v-for="option in datacenterOptions.dc_room"
                      :key="option"
                      :value="option"
                    >
                      {{ option }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-2">
                <label class="form-label">机柜编号</label>
                <Select v-model="datacenterForm.cabinet_no">
                  <SelectTrigger class="w-full">
                    <SelectValue placeholder="选择机柜编号" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      v-for="option in datacenterOptions.cabinet_no"
                      :key="option"
                      :value="option"
                    >
                      {{ option }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-2">
                <label class="form-label">起始 U 位</label>
                <Input v-model="datacenterForm.rack_u_start" placeholder="例如：12" />
              </div>
            </div>
            <div v-else class="space-y-2">
              <label class="form-label">使用人</label>
              <Select v-model="checkoutForm.user_id">
                <SelectTrigger class="w-full">
                  <SelectValue placeholder="选择用户" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="user in users" :key="user.id" :value="String(user.id)">
                    {{ user.full_name || user.username }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div v-else-if="actionType === 'checkin'" class="space-y-2">
            <label class="form-label">是否损坏</label>
            <div class="flex items-center gap-3 text-sm">
              <Switch v-model="checkinForm.damaged" />
              <span class="text-muted-foreground">{{ checkinForm.damaged ? "损坏" : "完好" }}</span>
            </div>
          </div>

          <div v-else-if="actionType === 'discard'" class="text-sm text-muted-foreground">
            资产将进入待报废状态，请确认是否继续。
          </div>

          <div v-else-if="actionType === 'unscrap'" class="space-y-2">
            <label class="form-label">取消原因</label>
            <Textarea v-model="unscrapForm.reason" placeholder="请填写原因" />
            <p class="text-xs text-muted-foreground">已报废资产需填写原因。</p>
          </div>
        </div>
        <DialogFooter class="mt-4">
          <Button variant="outline" type="button" @click="actionOpen = false">取消</Button>
          <Button type="button" @click="submitAction">确定</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <Drawer v-model:open="detailOpen">
      <DrawerContent class="w-full overflow-auto">
        <DrawerHeader>
          <DrawerTitle>资产详情</DrawerTitle>
          <DrawerDescription>查看资产基础信息与扩展信息。</DrawerDescription>
        </DrawerHeader>
        <div class="space-y-6 px-6 pb-8">
          <div class="rounded-lg border bg-muted/30">
            <div class="grid gap-2 p-4 md:grid-cols-3">
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">资产编号</div>
                <div class="text-sm text-muted-foreground">{{ detail?.asset_no || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">SN</div>
                <div class="text-sm text-muted-foreground">{{ detail?.sn || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">名称</div>
                <div class="text-sm text-muted-foreground">{{ detail?.name || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">分类</div>
                <div class="text-sm text-muted-foreground">{{ detail?.category || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">状态</div>
                <div class="text-sm text-muted-foreground">{{ statusLabels[detail?.status] || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">位置</div>
                <div class="text-sm text-muted-foreground">{{ detail?.location || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">采购原值</div>
                <div class="text-sm text-muted-foreground">{{ detail?.price ?? "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">采购日期</div>
                <div class="text-sm text-muted-foreground">{{ detail?.purchase_at || "-" }}</div>
              </div>
              <div class="flex items-start gap-3">
                <div class="w-24 text-sm font-medium">维保截止</div>
                <div class="text-sm text-muted-foreground">{{ detail?.warranty_at || "-" }}</div>
              </div>
            </div>
          </div>

          <div v-if="detailFields.length">
            <div class="text-sm font-semibold">扩展信息</div>
            <div class="mt-3 rounded-lg border bg-background">
              <div class="grid gap-2 p-4 md:grid-cols-3">
                <div v-for="field in detailFields" :key="field.id" class="flex items-start gap-3">
                  <div class="w-24 text-sm font-medium">{{ field.name }}</div>
                  <div
                    v-if="field.field_type === 'compound' && getCompoundMarkdownEntries(field, detailValues[field.id]).length"
                    class="space-y-1"
                  >
                    <div class="flex flex-wrap gap-1">
                      <Button
                        v-for="entry in getCompoundMarkdownEntries(field, detailValues[field.id])"
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
                      {{ `共 ${getCompoundMarkdownEntries(field, detailValues[field.id]).length} 篇文档` }}
                    </div>
                  </div>
                  <div v-else class="text-sm text-muted-foreground">
                    {{ formatFieldValue(field, detailValues[field.id]) }}
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
          <MdPreview editorId="asset-markdown-preview" :modelValue="markdownPreviewContent" language="zh-CN" />
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, defineAsyncComponent, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from "../components/ui/drawer";
import { Spinner } from "../components/ui/spinner";
import { Switch } from "../components/ui/switch";
import { Textarea } from "../components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from "../components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "../components/ui/dialog";
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
const actionOpen = ref(false);
const actionType = ref("");
const currentAsset = ref(null);
const users = ref([]);
const checkoutForm = ref({ user_id: "" });
const datacenterForm = ref({ dc_room: "", cabinet_no: "", rack_u_start: "" });
const datacenterFieldMap = ref({ dc_room: null, cabinet_no: null, rack_u_start: null });
const datacenterOptions = ref({ dc_room: [], cabinet_no: [] });
const checkinForm = ref({ damaged: false });
const unscrapForm = ref({ reason: "" });
const detail = ref(null);
const detailFields = ref([]);
const detailValues = ref({});
const markdownPreviewOpen = ref(false);
const markdownPreviewTitle = ref("");
const markdownPreviewContent = ref("");
const optionSourceCache = ref({});
const fieldOptionLabelMap = ref({});
const totalPages = computed(() => {
  const currentSize = Number(size.value) || 20;
  const pages = Math.ceil((Number(total.value) || 0) / currentSize);
  return Math.max(1, pages);
});

const statusLabels = {
  0: "闲置",
  1: "在用",
  2: "维修",
  3: "待报废",
  4: "已报废"
};

const load = async (resetPage = false) => {
  if (resetPage) {
    page.value = 1;
  }
  loading.value = true;
  try {
    const { data } = await api.get("/assets", {
      params: {
        page: page.value,
        size: size.value,
        q: q.value || null,
        status: status.value === "all" ? null : Number(status.value),
        scope: fixedScope.value || null
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
  await api.delete(`/assets/${pendingId.value}`);
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
  (fields || []).forEach((field) => {
    map[field.id] = buildOptionLabelMap(field);
  });
  fieldOptionLabelMap.value = map;
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

const openCompoundMarkdownPreview = (field, entry) => {
  markdownPreviewTitle.value = `${field?.name || "组合字段"} / ${entry.label}`;
  markdownPreviewContent.value = entry.content || "";
  markdownPreviewOpen.value = true;
};

const openDetail = async (id) => {
  detailOpen.value = true;
  detail.value = null;
  detailFields.value = [];
  detailValues.value = {};
  const { data } = await api.get(`/assets/${id}`);
  detail.value = data;
  if (data.category_id) {
    const [fieldsRes, valuesRes] = await Promise.all([
      api.get(`/categories/${data.category_id}/fields`, {
        params: { dept: fixedUsage.value || null }
      }),
      api.get(`/assets/${id}/fields`)
    ]);
    detailFields.value = fieldsRes.data;
    await preloadOptionSources(detailFields.value);
    buildFieldOptionMaps(detailFields.value);
    const map = {};
    for (const item of valuesRes.data) {
      map[item.field_id] = item.value;
    }
    detailValues.value = map;
  }
};

const actionTitle = computed(() => {
  if (actionType.value === "checkout") return checkoutLabel.value;
  if (actionType.value === "checkin") return checkinLabel.value;
  if (actionType.value === "discard") return "报废";
  if (actionType.value === "unscrap") return "取消报废";
  return "操作";
});

const loadUsers = async () => {
  const { data } = await api.get("/users");
  users.value = data;
};

const openAction = async (type, item) => {
  actionType.value = type;
  currentAsset.value = item;
  checkoutForm.value = { user_id: "" };
  checkinForm.value = { damaged: false };
  unscrapForm.value = { reason: "" };
  if (type === "checkout") {
    if (isDatacenter.value) {
      datacenterForm.value = { dc_room: "", cabinet_no: "", rack_u_start: "" };
      await loadDatacenterFields(item);
    } else if (users.value.length === 0) {
      await loadUsers();
    }
  }
  actionOpen.value = true;
};

const loadDatacenterFields = async (item) => {
  datacenterFieldMap.value = { dc_room: null, cabinet_no: null, rack_u_start: null };
  datacenterOptions.value = { dc_room: [], cabinet_no: [] };
  if (!item?.category_id) return;
  const { data } = await api.get(`/categories/${item.category_id}/fields`, {
    params: { dept: fixedUsage.value || null }
  });
  for (const field of data) {
    if (field.field_key === "dc_room") {
      datacenterFieldMap.value.dc_room = field.id;
      datacenterOptions.value.dc_room = (field.options || []).filter((item) => String(item || "").trim() !== "");
    }
    if (field.field_key === "cabinet_no") {
      datacenterFieldMap.value.cabinet_no = field.id;
      datacenterOptions.value.cabinet_no = (field.options || []).filter((item) => String(item || "").trim() !== "");
    }
    if (field.field_key === "rack_u_start") {
      datacenterFieldMap.value.rack_u_start = field.id;
    }
  }
};

const submitAction = async () => {
  if (!currentAsset.value) return;
  const id = currentAsset.value.id;
  if (actionType.value === "checkout") {
    if (isDatacenter.value) {
      if (!datacenterForm.value.dc_room || !datacenterForm.value.cabinet_no || !datacenterForm.value.rack_u_start) {
        return;
      }
      await api.post(`/assets/${id}/checkout`);
      const payload = [];
      if (datacenterFieldMap.value.dc_room) {
        payload.push({ field_id: datacenterFieldMap.value.dc_room, value: datacenterForm.value.dc_room });
      }
      if (datacenterFieldMap.value.cabinet_no) {
        payload.push({ field_id: datacenterFieldMap.value.cabinet_no, value: datacenterForm.value.cabinet_no });
      }
      if (datacenterFieldMap.value.rack_u_start) {
        payload.push({ field_id: datacenterFieldMap.value.rack_u_start, value: datacenterForm.value.rack_u_start });
      }
      if (payload.length) {
        await api.put(`/assets/${id}/fields`, payload);
      }
    } else {
      if (!checkoutForm.value.user_id) return;
      await api.post(`/assets/${id}/checkout`, null, {
        params: {
          user_id: Number(checkoutForm.value.user_id)
        }
      });
    }
  }
  if (actionType.value === "checkin") {
    await api.post(`/assets/${id}/checkin`, null, {
      params: { damaged: checkinForm.value.damaged }
    });
  }
  if (actionType.value === "discard") {
    await api.post(`/assets/${id}/discard`);
  }
  if (actionType.value === "unscrap") {
    const reason = unscrapForm.value.reason?.trim();
    if (currentAsset.value?.status === 4 && !reason) return;
    await api.post(`/assets/${id}/unscrap`, null, {
      params: { reason: reason || null }
    });
  }
  actionOpen.value = false;
  await load();
};

const route = useRoute();
const fixedUsage = computed(() => {
  if (route.path === "/assets/office") return "办公和业务";
  if (route.path === "/assets/datacenter") return "数据中心";
  return "";
});
const fixedScope = computed(() => {
  if (route.path === "/assets/office") return "office";
  if (route.path === "/assets/datacenter") return "datacenter";
  return "";
});
const isDatacenter = computed(() => fixedScope.value === "datacenter");
const checkoutLabel = computed(() => (isDatacenter.value ? "上架" : "领用"));
const checkinLabel = computed(() => (isDatacenter.value ? "下架" : "退库"));
const createLink = computed(() => {
  const dept = fixedUsage.value;
  if (dept) {
    return { path: "/assets/new", query: { dept } };
  }
  return { path: "/assets/new" };
});

onMounted(() => {
  if (fixedUsage.value) {
    localStorage.setItem("assetDeptScope", fixedUsage.value);
  }
  load(true);
});

watch(
  () => route.path,
  () => {
    if (fixedUsage.value) {
      localStorage.setItem("assetDeptScope", fixedUsage.value);
    }
    load(true);
  }
);
</script>

<style scoped></style>



