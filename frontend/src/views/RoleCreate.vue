<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-semibold">新建角色</h2>
        <p class="mt-1 text-sm text-muted-foreground">创建角色后可进入权限编辑。</p>
      </div>
      <Button variant="outline" @click="goBack">返回列表</Button>
    </div>

    <div class="card max-w-xl">
      <div class="space-y-4">
        <div class="space-y-2">
          <label class="text-sm font-medium">角色名称</label>
          <Input v-model="form.name" placeholder="例如：软件资产管理员" />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium">角色编码</label>
          <Input v-model="form.code" placeholder="例如：software_admin" />
        </div>
      </div>
      <div class="mt-6 flex items-center gap-3">
        <Button variant="outline" @click="goBack">取消</Button>
        <Button :disabled="creating" @click="submit">
          {{ creating ? "创建中..." : "创建" }}
        </Button>
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
import { toast } from "../components/ui/sonner";

const router = useRouter();
const creating = ref(false);
const form = reactive({
  name: "",
  code: "",
});

const goBack = () => {
  router.push("/roles");
};

const submit = async () => {
  if (!form.name.trim() || !form.code.trim()) {
    toast.error("请填写角色名称和编码");
    return;
  }
  creating.value = true;
  try {
    const { data } = await api.post("/roles", {
      name: form.name.trim(),
      code: form.code.trim(),
    });
    toast.success("角色已创建");
    router.push(`/roles/${data.id}/edit`);
  } catch (error) {
    toast.error(error?.response?.data?.detail || "创建失败");
  } finally {
    creating.value = false;
  }
};
</script>

<style scoped></style>



