<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-semibold">新建字典类型</h2>
        <p class="mt-1 text-sm text-muted-foreground">创建后进入字典项维护。</p>
      </div>
      <Button variant="outline" @click="goBack">返回列表</Button>
    </div>

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
      <div class="flex items-center gap-3">
        <Button variant="outline" @click="goBack">取消</Button>
        <Button :disabled="creating" @click="submit">{{ creating ? "创建中..." : "创建" }}</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Switch } from "../components/ui/switch";
import { toast } from "../components/ui/sonner";

const router = useRouter();
const creating = ref(false);
const form = reactive({
  name: "",
  code: "",
  scope: "global",
  description: "",
  sort_order: 0,
  is_active: true,
});

const goBack = () => {
  router.push("/dictionaries");
};

const submit = async () => {
  if (!form.name.trim() || !form.code.trim()) {
    toast.error("请填写名称和编码");
    return;
  }
  creating.value = true;
  try {
    const { data } = await api.post("/dictionaries/types", {
      ...form,
      name: form.name.trim(),
      code: form.code.trim(),
    });
    toast.success("已创建");
    router.push(`/dictionaries/${data.id}/edit`);
  } catch (error) {
    toast.error(error?.response?.data?.detail || "创建失败");
  } finally {
    creating.value = false;
  }
};
</script>

<style scoped></style>



