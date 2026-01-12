<template>
  <div class="flex min-h-[60vh] items-center justify-center">
    <div class="w-full max-w-sm rounded-lg border bg-background p-6 shadow-sm">
      <h2 class="mb-4 text-lg font-semibold">登录系统</h2>
      <div class="space-y-3">
        <input v-model="username" class="input" placeholder="用户名" />
        <input v-model="password" class="input" type="password" placeholder="密码" />
        <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
        <Button class="w-full" @click="onLogin">登录</Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import { Button } from "../components/ui/button";

const username = ref("admin");
const password = ref("admin123");
const auth = useAuthStore();
const router = useRouter();
const error = ref("");

const onLogin = async () => {
  error.value = "";
  try {
    await auth.login(username.value, password.value);
    router.push("/");
  } catch (err) {
    error.value = "登录失败，请检查账号密码或后端服务。";
  }
};
</script>

<style scoped></style>
