<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-semibold">编辑字典类型</h2>
        <p class="mt-1 text-sm text-muted-foreground">维护字典类型与字典项。</p>
      </div>
      <Button variant="outline" @click="goBack">返回列表</Button>
    </div>

    <div class="space-y-6">
      <div class="card space-y-4">
        <div class="text-sm font-semibold">字典类型</div>
        <div class="form-grid-2">
          <div class="form-field">
            <label class="form-label">名称</label>
            <Input v-model="form.name" placeholder="例如：数据中心" />
          </div>
          <div class="form-field">
            <label class="form-label">编码</label>
            <Input v-model="form.code" placeholder="例如：datacenter" />
          </div>
          <div class="form-field">
            <label class="form-label">适用范围</label>
            <Select v-model="form.scope">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="选择范围" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global">通用</SelectItem>
                <SelectItem value="office">办公硬件</SelectItem>
                <SelectItem value="datacenter">数据中心硬件</SelectItem>
                <SelectItem value="software">软件资产</SelectItem>
                <SelectItem value="system">系统资产</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="form-field">
            <label class="form-label">描述</label>
            <Input v-model="form.description" placeholder="可选" />
          </div>
          <div class="form-field">
            <label class="form-label">排序</label>
            <Input v-model="form.sort_order" type="number" />
          </div>
          <div class="form-field">
            <label class="form-label">启用</label>
            <div class="flex items-center gap-3 text-sm">
              <Switch v-model="form.is_active" />
              <span class="text-muted-foreground">启用</span>
            </div>
          </div>
        </div>
        <div>
          <Button :disabled="saving" @click="saveType">{{ saving ? "保存中..." : "保存类型" }}</Button>
        </div>
      </div>

      <div class="card space-y-4 edit-halo" :class="{ active: isEditingItem }">
        <div>
          <div class="text-sm font-semibold">字典项</div>
          <p class="text-xs text-muted-foreground">当前类型：{{ form.name || "-" }}</p>
        </div>
        <div class="form-grid-2">
          <div class="form-field">
            <label class="form-label">名称</label>
            <Input v-model="itemForm.name" placeholder="例如：机房A" />
          </div>
          <div class="form-field">
            <label class="form-label">值</label>
            <Input v-model="itemForm.value" placeholder="可选编码" />
          </div>
          <div class="form-field">
            <label class="form-label">排序</label>
            <Input v-model="itemForm.sort_order" type="number" />
          </div>
          <div class="form-field">
            <label class="form-label">启用</label>
            <div class="flex items-center gap-3 text-sm">
              <Switch v-model="itemForm.is_active" />
              <span class="text-muted-foreground">启用</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <Button @click="saveItem">保存字典项</Button>
          <Button variant="outline" @click="resetItemForm">清空</Button>
        </div>
      </div>
    </div>

    <div class="card">
      <table class="table">
        <thead>
          <tr>
            <th class="px-4 py-2">名称</th>
            <th class="px-4 py-2">值</th>
            <th class="px-4 py-2">状态</th>
            <th class="px-4 py-2 text-right">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" class="border-b">
            <td class="px-4 py-2">{{ item.name }}</td>
            <td class="px-4 py-2 text-sm text-muted-foreground">{{ item.value || "-" }}</td>
            <td class="px-4 py-2">{{ item.is_active ? "启用" : "停用" }}</td>
            <td class="px-4 py-2 text-right">
              <div class="flex items-center justify-end gap-2">
                <Button size="sm" variant="outline" @click="editItem(item)">编辑</Button>
                <AlertDialog>
                  <AlertDialogTrigger as-child>
                    <Button size="sm" variant="destructive">删除</Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>确认删除</AlertDialogTitle>
                      <AlertDialogDescription>删除后将无法恢复。</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>取消</AlertDialogCancel>
                      <AlertDialogAction @click="confirmDelete(item)">删除</AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td class="px-4 py-6 text-center text-sm text-muted-foreground" colspan="4">暂无字典项</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Switch } from "../components/ui/switch";
import { toast } from "../components/ui/sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../components/ui/alert-dialog";

const route = useRoute();
const router = useRouter();
const items = ref([]);
const saving = ref(false);

const form = reactive({
  id: null,
  name: "",
  code: "",
  scope: "global",
  description: "",
  sort_order: 0,
  is_active: true,
});

const itemForm = reactive({
  id: null,
  name: "",
  value: "",
  sort_order: 0,
  is_active: true,
});

const typeId = computed(() => Number(route.params.id));
const isEditingItem = computed(() => Boolean(itemForm.id));

const goBack = () => {
  router.push("/dictionaries");
};

const loadType = async () => {
  const { data } = await api.get("/dictionaries/types");
  const found = Array.isArray(data) ? data.find((item) => item.id === typeId.value) : null;
  if (!found) {
    toast.error("未找到字典类型");
    return;
  }
  Object.assign(form, found);
};

const loadItems = async () => {
  if (!form.code) return;
  const { data } = await api.get("/dictionaries/items", { params: { type: form.code } });
  items.value = Array.isArray(data) ? data : [];
};

const saveType = async () => {
  if (!form.name.trim() || !form.code.trim()) {
    toast.error("请填写名称和编码");
    return;
  }
  saving.value = true;
  try {
    await api.put(`/dictionaries/types/${form.id}`, {
      ...form,
      name: form.name.trim(),
      code: form.code.trim(),
    });
    toast.success("类型已保存");
  } catch (error) {
    toast.error(error?.response?.data?.detail || "保存失败");
  } finally {
    saving.value = false;
  }
};

const resetItemForm = () => {
  itemForm.id = null;
  itemForm.name = "";
  itemForm.value = "";
  itemForm.sort_order = 0;
  itemForm.is_active = true;
};

const saveItem = async () => {
  if (!itemForm.name.trim()) {
    toast.error("请填写名称");
    return;
  }
  try {
    if (itemForm.id) {
      await api.put(`/dictionaries/items/${itemForm.id}`, {
        name: itemForm.name,
        value: itemForm.value,
        sort_order: itemForm.sort_order,
        is_active: itemForm.is_active,
      });
    } else {
      await api.post("/dictionaries/items", {
        ...itemForm,
        type_id: form.id,
      });
    }
    toast.success("字典项已保存");
    await loadItems();
    resetItemForm();
  } catch (error) {
    toast.error(error?.response?.data?.detail || "保存失败");
  }
};

const editItem = (item) => {
  itemForm.id = item.id;
  itemForm.name = item.name;
  itemForm.value = item.value || "";
  itemForm.sort_order = item.sort_order || 0;
  itemForm.is_active = item.is_active;
};

const confirmDelete = async (item) => {
  try {
    await api.delete(`/dictionaries/items/${item.id}`);
    toast.success("已删除");
    await loadItems();
  } catch (error) {
    toast.error(error?.response?.data?.detail || "删除失败");
  }
};

onMounted(async () => {
  await loadType();
  await loadItems();
});
</script>

<style scoped>
.edit-halo {
  position: relative;
  overflow: hidden;
  --glow-color: #7cff8a;
  --secondary-glow: #75ed5b;
  --accent-glow: #9bff23;
  --animation-speed: 3s;
  --border-width: 2px;
  --halo-radius: 0.75rem;
}

.edit-halo::before,
.edit-halo::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: var(--halo-radius);
  pointer-events: none;
  opacity: 0;
}

.edit-halo.active::before {
  opacity: 1;
  width: 180%;
  height: 280%;
  left: -40%;
  top: -90%;
  background: conic-gradient(
    transparent,
    var(--glow-color),
    var(--accent-glow),
    var(--secondary-glow),
    transparent 25%
  );
  animation: halo-rotate var(--animation-speed) linear infinite;
}

.edit-halo.active::after {
  opacity: 1;
  inset: var(--border-width);
  background: var(--card-bg, var(--background, #0f172a));
  border-radius: calc(var(--halo-radius) - var(--border-width));
  z-index: 1;
}

.edit-halo > * {
  position: relative;
  z-index: 2;
}

@keyframes halo-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>


