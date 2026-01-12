<template>
  <div class="theme-green min-h-screen bg-muted/40">
    <div class="theme-container">
      <div v-if="isLogin" class="p-6">
        <router-view />
      </div>
      <div v-else class="flex">
        <aside class="hidden min-h-screen w-64 border-r bg-background px-4 py-6 md:block">
          <div class="text-lg font-semibold tracking-wide">ITAM</div>
          <nav class="mt-6 space-y-1">
            <div class="nav-title">总览</div>
            <RouterLink class="nav-link" to="/">仪表盘</RouterLink>

            <div class="nav-title">资产管理</div>
            <RouterLink class="nav-link" to="/assets">资产台账</RouterLink>
            <RouterLink class="nav-link" to="/asset-types">资产类型/字段</RouterLink>
            <RouterLink class="nav-link" to="/assets/import">批量导入</RouterLink>
            <RouterLink class="nav-link" to="/assets/flow">领用/退库/调拨</RouterLink>
            <RouterLink class="nav-link" to="/maintenance">维保与报修</RouterLink>
            <RouterLink class="nav-link" to="/scrap">报废管理</RouterLink>

            <div class="nav-title">软件资产</div>
            <RouterLink class="nav-link" to="/licenses">授权管理</RouterLink>

            <div class="nav-title">盘点</div>
            <RouterLink class="nav-link" to="/stocktakes">盘点任务</RouterLink>
            <RouterLink class="nav-link" to="/scan">扫码工具</RouterLink>

            <div class="nav-title">系统</div>
            <RouterLink class="nav-link" to="/users">用户管理</RouterLink>
            <RouterLink class="nav-link" to="/roles">角色权限</RouterLink>
            <RouterLink class="nav-link" to="/logs">操作审计</RouterLink>
            <RouterLink class="nav-link" to="/reports">财务报表</RouterLink>
            <RouterLink class="nav-link" to="/settings">系统设置</RouterLink>
          </nav>
        </aside>

        <main class="flex-1">
          <header class="flex items-center justify-between border-b bg-background px-6 py-4">
            <div class="text-base font-semibold">IT 资产管理系统</div>
            <div class="text-sm text-muted-foreground">{{ auth.username || "未登录" }}</div>
          </header>

          <section class="p-6">
            <router-view />
          </section>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const auth = useAuthStore();
const isLogin = computed(() => route.path === "/login");
</script>

<style scoped>
.nav-link {
  display: block;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--foreground);
}

.nav-link.router-link-active {
  background: var(--muted);
}

.nav-title {
  margin-top: 12px;
  padding: 8px 12px 4px;
  font-size: 12px;
  color: var(--muted-foreground);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
</style>
