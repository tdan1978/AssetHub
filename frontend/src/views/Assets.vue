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
          <Button :disabled="loading" @click="load">查询</Button>
          <RouterLink to="/assets/new">
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
            <th class="px-4 py-2">用途</th>
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
            <td class="px-4 py-2">{{ item.dept }}</td>
            <td class="px-4 py-2">
              <div class="flex gap-2" @click.stop>
                <DropdownMenu>
                  <DropdownMenuTrigger as-child>
                    <Button size="sm" variant="outline">操作</Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" class="w-40">
                    <DropdownMenuItem :disabled="item.status !== 0" @click="openAction('checkout', item)">
                      领用
                    </DropdownMenuItem>
                    <DropdownMenuItem :disabled="item.status !== 1" @click="openAction('checkin', item)">
                      退库
                    </DropdownMenuItem>
                    <DropdownMenuItem :disabled="item.status !== 1" @click="openAction('transfer', item)">
                      调拨
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
                <Button size="sm" variant="outline" @click.stop="askDelete(item.id)">删除</Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
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
            <div class="space-y-2">
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
            <div class="space-y-2">
              <label class="form-label">用途</label>
              <Select v-model="checkoutForm.dept">
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

          <div v-else-if="actionType === 'checkin'" class="space-y-2">
            <label class="form-label">是否损坏</label>
            <div class="flex items-center gap-3 text-sm">
              <Switch v-model="checkinForm.damaged" />
              <span class="text-muted-foreground">{{ checkinForm.damaged ? "损坏" : "完好" }}</span>
            </div>
          </div>

          <div v-else-if="actionType === 'transfer'" class="space-y-2">
            <label class="form-label">目标用途</label>
            <Select v-model="transferForm.dept">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="选择用途" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="办公和业务">办公和业务</SelectItem>
                <SelectItem value="数据中心">数据中心</SelectItem>
              </SelectContent>
            </Select>
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
          <DrawerDescription>查看资产基础信息与自定义字段。</DrawerDescription>
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
                <div class="w-24 text-sm font-medium">用途</div>
                <div class="text-sm text-muted-foreground">{{ detail?.dept || "-" }}</div>
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
            <div class="text-sm font-semibold">自定义字段</div>
            <div class="mt-3 rounded-lg border bg-background">
              <div class="grid gap-2 p-4 md:grid-cols-3">
                <div v-for="field in detailFields" :key="field.id" class="flex items-start gap-3">
                  <div class="w-24 text-sm font-medium">{{ field.name }}</div>
                  <div class="text-sm text-muted-foreground">
                    {{ formatFieldValue(detailValues[field.id]) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
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

const items = ref([]);
const q = ref("");
const status = ref("all");
const loading = ref(false);
const confirmOpen = ref(false);
const pendingId = ref(null);
const detailOpen = ref(false);
const actionOpen = ref(false);
const actionType = ref("");
const currentAsset = ref(null);
const users = ref([]);
const checkoutForm = ref({ user_id: "", dept: "" });
const transferForm = ref({ dept: "" });
const checkinForm = ref({ damaged: false });
const unscrapForm = ref({ reason: "" });
const detail = ref(null);
const detailFields = ref([]);
const detailValues = ref({});

const statusLabels = {
  0: "闲置",
  1: "在用",
  2: "维修",
  3: "待报废",
  4: "已报废"
};

const load = async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/assets", {
      params: {
        page: 1,
        size: 20,
        q: q.value || null,
        status: status.value === "all" ? null : Number(status.value)
      }
    });
    items.value = data.items;
  } finally {
    loading.value = false;
  }
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

const formatFieldValue = (value) => {
  if (Array.isArray(value)) return value.join("，");
  if (value === null || value === undefined || value === "") return "-";
  return value;
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
      api.get(`/categories/${data.category_id}/fields`),
      api.get(`/assets/${id}/fields`)
    ]);
    detailFields.value = fieldsRes.data;
    const map = {};
    for (const item of valuesRes.data) {
      map[item.field_id] = item.value;
    }
    detailValues.value = map;
  }
};

const actionTitle = computed(() => {
  if (actionType.value === "checkout") return "领用";
  if (actionType.value === "checkin") return "退库";
  if (actionType.value === "transfer") return "调拨";
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
  checkoutForm.value = { user_id: "", dept: "" };
  transferForm.value = { dept: "" };
  checkinForm.value = { damaged: false };
  unscrapForm.value = { reason: "" };
  if (type === "checkout" && users.value.length === 0) {
    await loadUsers();
  }
  actionOpen.value = true;
};

const submitAction = async () => {
  if (!currentAsset.value) return;
  const id = currentAsset.value.id;
  if (actionType.value === "checkout") {
    if (!checkoutForm.value.user_id) return;
    await api.post(`/assets/${id}/checkout`, null, {
      params: {
        user_id: Number(checkoutForm.value.user_id),
        dept: checkoutForm.value.dept || null
      }
    });
  }
  if (actionType.value === "checkin") {
    await api.post(`/assets/${id}/checkin`, null, {
      params: { damaged: checkinForm.value.damaged }
    });
  }
  if (actionType.value === "transfer") {
    if (!transferForm.value.dept) return;
    await api.post(`/assets/${id}/transfer`, null, {
      params: { dept: transferForm.value.dept }
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

onMounted(load);
</script>

<style scoped></style>
