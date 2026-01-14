<template>
  <div class="theme-green min-h-screen bg-muted/40">
    <div class="theme-container">
      <div v-if="isLogin" class="p-6">
        <router-view />
      </div>
      <div v-else class="flex">
        <Sidebar class="hidden md:flex" :collapsed="isSidebarCollapsed">
          <SidebarHeader>
            <div class="flex items-center gap-3">
              <img
                :src="logoUrl"
                alt="AssetHub"
                class="rounded-lg object-contain"
                :class="isSidebarCollapsed ? 'h-7 w-7' : 'h-[40px] w-auto'"
              />
              <div v-if="!isSidebarCollapsed" class="flex flex-col justify-center">
                <div class="text-[1.2rem] font-bold italic tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-lime-500 to-green-600">
                  AssetHub
                </div>
                <div class="text-[0.65rem] text-muted-foreground">资产管理系统</div>
              </div>
            </div>
            <SidebarTrigger @click="toggleSidebar">
              <PanelLeft class="h-4 w-4" />
            </SidebarTrigger>
          </SidebarHeader>
          <SidebarContent>
            <nav class="space-y-3">
              <SidebarGroup v-for="group in menuGroups" :key="group.title">
                <SidebarGroupLabel v-if="!isSidebarCollapsed">{{ group.title }}</SidebarGroupLabel>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <Button
                      variant="ghost"
                      class="sidebar-group"
                      @click="toggleGroup(group.title)"
                    >
                      <component :is="group.icon" class="h-4 w-4" />
                      <span v-if="!isSidebarCollapsed" class="flex-1 text-left text-sm font-medium">
                        {{ group.title }}
                      </span>
                      <ChevronDown
                        v-if="!isSidebarCollapsed"
                        class="h-4 w-4 transition-transform"
                        :class="{ 'rotate-180': isGroupOpen(group.title) }"
                      />
                    </Button>
                  </SidebarMenuItem>
                  <div v-show="!isSidebarCollapsed && isGroupOpen(group.title)" class="space-y-1 pl-6">
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
                </SidebarMenu>
              </SidebarGroup>
            </nav>
          </SidebarContent>
        </Sidebar>

        <main class="flex-1">
          <header class="flex items-center justify-between border-b bg-background px-6 py-4">
            <div class="text-base font-semibold">AssetHub 资产管理系统</div>
            <div class="flex items-center gap-2">
              <DropdownMenu v-model:open="notificationOpen">
                <DropdownMenuTrigger as-child>
                  <Button variant="ghost" class="relative h-9 w-9 p-0">
                    <Bell class="h-4 w-4" />
                    <span
                      v-if="unreadCount"
                      class="absolute -right-1 -top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-semibold text-white"
                    >
                      {{ unreadCount }}
                    </span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" class="w-80">
                  <div class="px-3 py-2 text-sm font-semibold">系统消息</div>
                  <div v-if="notificationsLoading" class="flex items-center gap-2 px-3 py-3 text-sm text-muted-foreground">
                    <Spinner class="size-4" />
                    加载中...
                  </div>
                  <div v-else-if="!visibleNotifications.length" class="px-3 py-3 text-sm text-muted-foreground">
                    暂无消息
                  </div>
                  <div v-else class="max-h-80 overflow-auto">
                    <div
                      v-for="item in visibleNotifications"
                      :key="item.id"
                      class="border-t px-3 py-2 text-sm"
                    >
                      <div class="flex items-start justify-between gap-2">
                        <div class="space-y-1">
                          <div class="font-medium text-foreground">{{ item.title }}</div>
                          <div class="text-xs text-muted-foreground">{{ item.message }}</div>
                          <div v-if="item.due_date" class="text-xs text-muted-foreground">
                            到期日：{{ item.due_date }}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          class="h-7 px-2 text-xs"
                          @click="markRead(item.id)"
                        >
                          已读
                        </Button>
                      </div>
                    </div>
                  </div>
                </DropdownMenuContent>
              </DropdownMenu>

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
            </div>
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
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "./api/client";
import { useAuthStore } from "./stores/auth";
import logoUrl from "./assets/logo.png";
import { Alert, AlertDescription, AlertTitle } from "./components/ui/alert";
import { Avatar, AvatarFallback, AvatarImage } from "./components/ui/avatar";
import { Button } from "./components/ui/button";
import { Spinner } from "./components/ui/spinner";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarTrigger
} from "./components/ui/sidebar";
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
  Bell,
  Boxes,
  ClipboardCheck,
  ClipboardList,
  FileBarChart,
  FileSearch,
  Gauge,
  KeyRound,
  LayoutDashboard,
  ListTree,
  PanelLeft,
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
      { label: "软件资产台账", to: "/licenses", icon: KeyRound },
      { label: "字段分类", to: "/software-field-categories", icon: ListTree }
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
    title: "系统资产管理",
    icon: FileSearch,
    items: [
      { label: "系统资产台账", to: "/systems", icon: ClipboardList },
      { label: "字段分类", to: "/system-field-categories", icon: ListTree }
    ]
  },
  {
    title: "系统",
    icon: Settings,
    items: [
      { label: "系统消息", to: "/notifications", icon: Bell },
      { label: "用户管理", to: "/users", icon: Users },
      { label: "角色权限", to: "/roles", icon: Shield },
      { label: "操作审计", to: "/logs", icon: FileSearch },
      { label: "财务报表", to: "/reports", icon: FileBarChart },
      { label: "系统设置", to: "/settings", icon: Settings }
    ]
  }
];

const openGroups = ref([]);
const isSidebarCollapsed = ref(false);
const notifications = ref([]);
const readNotificationIds = ref(new Set());
const notificationsLoading = ref(false);
const notificationOpen = ref(false);
const notificationTimer = ref(null);

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

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
  if (isSidebarCollapsed.value) {
    openGroups.value = [];
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
    if (isSidebarCollapsed.value) {
      openGroups.value = [];
    }
  }
);

const loadNotifications = async () => {
  notificationsLoading.value = true;
  try {
    const { data } = await api.get("/notifications");
    notifications.value = data;
  } finally {
    notificationsLoading.value = false;
  }
};

watch(notificationOpen, (open) => {
  if (open) {
    loadNotifications();
  }
});

const visibleNotifications = computed(() =>
  notifications.value.filter((item) => !readNotificationIds.value.has(item.id))
);

const unreadCount = computed(() => visibleNotifications.value.length);

const persistReadIds = (nextSet) => {
  readNotificationIds.value = new Set(nextSet);
  localStorage.setItem("assethub_read_notifications", JSON.stringify([...readNotificationIds.value]));
  window.dispatchEvent(new Event("assethub-notifications-updated"));
};

const markRead = (id) => {
  const next = new Set(readNotificationIds.value);
  next.add(id);
  persistReadIds(next);
};

onMounted(() => {
  const cached = localStorage.getItem("assethub_read_notifications");
  if (cached) {
    try {
      readNotificationIds.value = new Set(JSON.parse(cached));
    } catch {
      readNotificationIds.value = new Set();
    }
  }
  loadNotifications();
  notificationTimer.value = setInterval(loadNotifications, 60000);
  window.addEventListener("assethub-notifications-updated", reloadReadIds);
  window.addEventListener("storage", handleStorageSync);
});

onBeforeUnmount(() => {
  if (notificationTimer.value) {
    clearInterval(notificationTimer.value);
  }
  window.removeEventListener("assethub-notifications-updated", reloadReadIds);
  window.removeEventListener("storage", handleStorageSync);
});

const reloadReadIds = () => {
  const cached = localStorage.getItem("assethub_read_notifications");
  if (!cached) {
    readNotificationIds.value = new Set();
    return;
  }
  try {
    readNotificationIds.value = new Set(JSON.parse(cached));
  } catch {
    readNotificationIds.value = new Set();
  }
};

const handleStorageSync = (event) => {
  if (event.key === "assethub_read_notifications") {
    reloadReadIds();
  }
};

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
