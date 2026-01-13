<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold">新增授权</h2>
          <p class="text-sm text-muted-foreground">录入软件授权信息。</p>
        </div>
        <RouterLink to="/licenses">
          <Button variant="outline">返回列表</Button>
        </RouterLink>
      </div>
    </div>

    <div class="card">
      <div class="grid gap-3 md:grid-cols-2">
        <Input v-model="form.name" placeholder="软件名称" />
        <Input v-model="form.total_qty" type="number" min="1" placeholder="总数" />
        <Textarea v-model="form.license_key" class="md:col-span-2" placeholder="授权密钥" />
      </div>
      <div class="mt-4">
        <Button @click="save">保存</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";

const router = useRouter();
const form = ref({ name: "", license_key: "", total_qty: 1, used_qty: 0 });

const save = async () => {
  await api.post("/licenses", form.value);
  router.push("/licenses");
};
</script>
