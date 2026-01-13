<template>
  <div class="theme-green min-h-screen bg-muted/40">
    <div class="theme-container">
      <div v-if="isLogin" class="p-6">
        <router-view />
      </div>
      <div v-else class="flex">
        <aside class="hidden min-h-screen w-72 border-r bg-background px-4 py-6 md:block">
          <div class="flex items-center gap-3 px-2">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-sm font-semibold text-primary-foreground">
              IT
            </div>
            <div class="space-y-1">
              <div class="text-sm font-semibold tracking-wide">ITAM</div>
              <div class="text-xs text-muted-foreground">资产管理系统</div>
            </div>
          </div>
          <nav class="mt-6 space-y-3">
            <div v-for="group in menuGroups" :key="group.title" class="space-y-1">
              <Button
                variant="ghost"
                class="sidebar-group"
                @click="toggleGroup(group.title)"
              >
                <component :is="group.icon" class="h-4 w-4" />
                <span class="flex-1 text-left text-sm font-medium">{{ group.title }}</span>
                <ChevronDown
                  class="h-4 w-4 transition-transform"
                  :class="{ 'rotate-180': isGroupOpen(group.title) }"
                />
              </Button>
              <div v-show="isGroupOpen(group.title)" class="space-y-1 pl-6">
                <RouterLink
                  v-for="item in group.items"
                  :key="item.to"
                  :to="item.to"
                  class="sidebar-link"
                  :class="{ 'sidebar-link-active': isActive(item.to) }"
                >
                  <component :is="item.icon" class="h-4 w-4" />
                  <span class="text-sm">{{ item.label }}</span>
                </RouterLink>
              </div>
            </div>
          </nav>
        </aside>

        <main class="flex-1">
          <header class="flex items-center justify-between border-b bg-background px-6 py-4">
            <div class="text-base font-semibold">IT 资产管理系统</div>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <Button variant="ghost" class="flex items-center gap-2 px-2">
                  <Avatar class="h-8 w-8">
                    <AvatarImage :src="avatarUrl" alt="" />
                    <AvatarFallback>{{ userInitial }}</AvatarFallback>
                  </Avatar>
                  <span class="text-sm font-medium text-foreground">{{ auth.username || "未登录" }}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" class="w-40">
                <DropdownMenuItem @select="openChangePassword">修改密码</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem variant="destructive" @select="handleLogout">退出</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </header>

          <section class="p-6">
            <router-view />
          </section>

          <Dialog v-model:open="changePasswordOpen">
            <DialogContent class="sm:max-w-[420px]">
              <DialogHeader>
                <DialogTitle>修改密码</DialogTitle>
                <DialogDescription>为安全起见，请输入旧密码并设置新密码。</DialogDescription>
              </DialogHeader>
              <div class="space-y-4">
                <div class="space-y-2">
                  <label class="text-sm font-medium">旧密码</label>
                  <Input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    autocomplete="current-password"
                  />
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-medium">新密码</label>
                  <Input
                    v-model="passwordForm.newPassword"
                    type="password"
                    autocomplete="new-password"
                  />
                </div>
                <div class="space-y-2">
                  <label class="text-sm font-medium">确认新密码</label>
                  <Input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    autocomplete="new-password"
                  />
                </div>
              </div>
              <Alert v-if="passwordError" variant="destructive" class="mt-4">
                <AlertTitle>修改失败</AlertTitle>
                <AlertDescription>{{ passwordError }}</AlertDescription>
              </Alert>
              <Alert v-else-if="passwordSuccess" class="mt-4">
                <AlertTitle>修改成功</AlertTitle>
                <AlertDescription>{{ passwordSuccess }}</AlertDescription>
              </Alert>
              <DialogFooter class="mt-4">
                <Button variant="outline" type="button" @click="changePasswordOpen = false">取消</Button>
                <Button type="button" :disabled="isSavingPassword" @click="submitChangePassword">
                  {{ isSavingPassword ? "提交中..." : "提交" }}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "./api/client";
import { useAuthStore } from "./stores/auth";
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert";
import { Avatar, AvatarFallback, AvatarImage } from "./components/ui/avatar";
import { Button } from "./components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "./components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "./components/ui/dialog";
import { Input } from "./components/ui/input";
import {
  ArrowLeftRight,
  Boxes,
  ClipboardCheck,
  ClipboardList,
  FileBarChart,
  FileSearch,
  Gauge,
  KeyRound,
  LayoutDashboard,
  ListTree,
  QrCode,
  Settings,
  Shield,
  Trash2,
  Upload,
  Users,
  Wrench,
  Package
} from "lucide-vue-next";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const isLogin = computed(() => route.path === "/login");

const menuGroups = [
  {
    title: "总览",
    icon: Gauge,
    items: [
      { label: "仪表盘", to: "/", icon: LayoutDashboard }
    ]
  },
  {
    title: "硬件资产管理",
    icon: Boxes,
    items: [
      { label: "资产台账", to: "/assets", icon: Package },
      { label: "资产类型/字段", to: "/asset-types", icon: ListTree },
      { label: "批量导入", to: "/assets/import", icon: Upload },
      { label: "领用/退库/调拨", to: "/assets/flow", icon: ArrowLeftRight },
      { label: "维保与报修", to: "/maintenance", icon: Wrench },
      { label: "报废管理", to: "/scrap", icon: Trash2 }
    ]
  },
  {
    title: "软件资产",
    icon: KeyRound,
    items: [
      { label: "授权管理", to: "/licenses", icon: KeyRound }
    ]
  },
  {
    title: "盘点",
    icon: ClipboardList,
    items: [
      { label: "盘点任务", to: "/stocktakes", icon: ClipboardCheck },
      { label: "扫码工具", to: "/scan", icon: QrCode }
    ]
  },
  {
    title: "系统",
    icon: Settings,
    items: [
      { label: "用户管理", to: "/users", icon: Users },
      { label: "角色权限", to: "/roles", icon: Shield },
      { label: "操作审计", to: "/logs", icon: FileSearch },
      { label: "财务报表", to: "/reports", icon: FileBarChart },
      { label: "系统设置", to: "/settings", icon: Settings }
    ]
  }
];

const openGroups = ref(menuGroups.map((group) => group.title));

const changePasswordOpen = ref(false);
const isSavingPassword = ref(false);
const passwordError = ref("");
const passwordSuccess = ref("");
const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: ""
});

const userInitial = computed(() => {
  const name = (auth.username || "").trim();
  return name ? name.slice(0, 1).toUpperCase() : "U";
});

const avatarUrl = computed(() => "");

const isActive = (to) => {
  if (to === "/") {
    return route.path === "/";
  }
  return route.path.startsWith(to);
};

const isGroupOpen = (title) => openGroups.value.includes(title);

const toggleGroup = (title) => {
  if (isGroupOpen(title)) {
    openGroups.value = openGroups.value.filter((item) => item !== title);
  } else {
    openGroups.value = [...openGroups.value, title];
  }
};

const resetPasswordForm = () => {
  passwordForm.oldPassword = "";
  passwordForm.newPassword = "";
  passwordForm.confirmPassword = "";
  passwordError.value = "";
  passwordSuccess.value = "";
};

watch(changePasswordOpen, (open) => {
  if (open) {
    resetPasswordForm();
  }
});

watch(
  () => route.path,
  () => {
    const activeGroup = menuGroups.find((group) =>
      group.items.some((item) => isActive(item.to))
    );
    if (activeGroup && !isGroupOpen(activeGroup.title)) {
      openGroups.value = [...openGroups.value, activeGroup.title];
    }
  }
);

const openChangePassword = () => {
  changePasswordOpen.value = true;
};

const handleLogout = () => {
  auth.logout();
  router.push("/login");
};

const submitChangePassword = async () => {
  passwordError.value = "";
  passwordSuccess.value = "";

  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    passwordError.value = "请填写旧密码和新密码。";
    return;
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = "两次输入的新密码不一致。";
    return;
  }

  isSavingPassword.value = true;
  try {
    await api.post("/auth/change-password", {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    });
    passwordSuccess.value = "密码已更新。";
    passwordForm.oldPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
  } catch (error) {
    passwordError.value =
      error?.response?.data?.detail || "修改密码失败，请稍后重试。";
  } finally {
    isSavingPassword.value = false;
  }
};
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

.sidebar-group {
  width: 100%;
  justify-content: flex-start;
  gap: 10px;
  padding-left: 10px;
  padding-right: 10px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 14px;
  color: var(--foreground);
}

.sidebar-link-active {
  background: var(--accent);
  color: var(--accent-foreground);
}
</style>
