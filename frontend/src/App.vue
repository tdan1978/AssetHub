<template>
  <div class="theme-green min-h-screen bg-muted/40">
    <Toaster />
    <div class="theme-container">
      <div v-if="isLogin" class="p-0">
        <router-view />
      </div>
      <div v-else class="flex h-screen overflow-hidden">
        <Sidebar class="hidden md:flex h-screen overflow-y-auto" :collapsed="isSidebarCollapsed">
          <SidebarHeader>
            <div v-if="!isSidebarCollapsed" class="flex items-center gap-3">
              <img
                :src="logoUrl"
                alt="AssetHub"
                class="h-[32px] w-[70px] rounded-lg object-contain"
              />
              <div class="flex flex-col justify-center">
                <div class="text-[1.2rem] font-black italic tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-lime-500 to-green-600">
                  AssetHub
                </div>
                <div class="text-[0.65rem] text-muted-foreground">IT Asset Management System</div>
              </div>
            </div>
            <SidebarTrigger @click="toggleSidebar">
              <PanelLeft class="h-4 w-4" />
            </SidebarTrigger>
          </SidebarHeader>
          <SidebarContent>
            <nav class="space-y-3">
              <SidebarGroup v-for="group in visibleMenuGroups" :key="group.title">
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
                      class="sidebar-link sidebar-link-sub hover:text-foreground"
                      :class="[{ 'sidebar-link-active': isActive(item.to) }, { 'sidebar-link-demo': item.demo }]"
                    >
                      <component :is="item.icon" class="h-4 w-4" />
                      <span class="sidebar-link-text">{{ item.label }}</span>
                      <span v-if="item.demo" class="sidebar-demo-badge">demo</span>
                    </RouterLink>
                  </div>
                </SidebarMenu>
              </SidebarGroup>
            </nav>
          </SidebarContent>
          <div class="border-t px-3 py-3 text-[11px] text-muted-foreground">
            © 2026 AssetHub Contributors
          </div>
        </Sidebar>

        <main class="flex-1 flex flex-col h-screen overflow-hidden">
          <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-background px-6 py-4">
            <div v-if="isSidebarCollapsed" class="flex items-center gap-3">
              <img
                :src="logoUrl"
                alt="AssetHub"
                class="h-[32px] w-[70px] rounded-lg object-contain"
              />
              <div class="flex flex-col justify-center">
                <div class="text-[1.2rem] font-bold italic tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-lime-500 to-green-600">
                  AssetHub
                </div>
                <div class="text-[0.65rem] text-muted-foreground">IT Asset Management System</div>
              </div>
            </div>
            <div v-else />
            <div class="flex items-center gap-2">
              <DropdownMenu v-if="canViewNotifications" v-model:open="notificationOpen">
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
                    <span class="text-sm font-medium text-foreground">{{ auth.fullName || auth.username || "未登录" }}</span>
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

          <section class="flex-1 overflow-y-auto p-6">
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
import { Toaster } from "./components/ui/sonner";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
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
  ChevronDown,
  ClipboardCheck,
  ClipboardList,
  FileBarChart,
  FileSearch,
  Gauge,
  Database,
  KeyRound,
  LayoutDashboard,
  ListTree,
  Monitor,
  PanelLeft,
  QrCode,
  Server,
  Settings,
  Shield,
  Trash2,
  Upload,
  UserCog,
  Users,
  UsersRound,
  Wrench,
  Package
} from "lucide-vue-next";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const isLogin = computed(() => route.path === "/login");
const roleCode = computed(() => auth.roleCode || localStorage.getItem("roleCode") || "");
const permissionSet = computed(() => new Set(auth.permissions || []));
const hasPermission = (resource, action = "view") => {
  if (!resource) return true;
  if (!auth.permissionsLoaded && auth.token) return true;
  if (roleCode.value === "super_admin") return true;
  return permissionSet.value.has(`${resource}:${action}`);
};
const hasAnyPermission = (items = []) => items.some((item) => hasPermission(item.resource, item.action || "view"));
const hasMenuPermission = (permission) => {
  if (!permission) return true;
  if (permission.any) return hasAnyPermission(permission.any);
  return hasPermission(permission.resource, permission.action || "view");
};
const canViewNotifications = computed(() => auth.permissionsLoaded && hasPermission("notifications", "view"));

const menuGroups = [
  {
    title: "总览",
    icon: Gauge,
    items: [
      { label: "仪表盘", to: "/", icon: LayoutDashboard, permission: { resource: "dashboard", action: "view" } }
    ]
  },
  {
    title: "硬件资产管理",
    icon: Boxes,
    items: [
  { label: "办公资产台账", to: "/assets/office", icon: Monitor, permission: { resource: "office_hardware_assets", action: "view" } },
  { label: "数据中心资产台账", to: "/assets/datacenter", icon: Server, permission: { resource: "datacenter_hardware_assets", action: "view" } },
      { label: "资产类型/字段", to: "/asset-types", icon: ListTree, permission: { resource: "asset_types", action: "view" } },
      {
        label: "批量导入",
        to: "/assets/import",
        icon: Upload,
        demo: true,
        permission: {
          any: [
            { resource: "office_hardware_assets", action: "create" },
            { resource: "datacenter_hardware_assets", action: "create" }
          ]
        }
      },
      {
        label: "领用/退库/调拨",
        to: "/assets/flow",
        icon: ArrowLeftRight,
        demo: true,
        permission: {
          any: [
            { resource: "office_hardware_assets", action: "update" },
            { resource: "datacenter_hardware_assets", action: "update" }
          ]
        }
      },
      { label: "维保与报修", to: "/maintenance", icon: Wrench, demo: true, permission: { resource: "maintenance", action: "view" } },
      { label: "报废管理", to: "/scrap", icon: Trash2, demo: true, permission: { resource: "scrap", action: "view" } }
    ]
  },
  {
    title: "软件资产",
    icon: KeyRound,
    items: [
      { label: "软件资产台账", to: "/licenses", icon: KeyRound, permission: { resource: "software_assets", action: "view" } },
      { label: "字段分类", to: "/software-field-categories", icon: ListTree, permission: { resource: "software_fields", action: "view" } }
    ]
  },
  {
    title: "系统资产管理",
    icon: FileSearch,
    items: [
      { label: "系统资产台账", to: "/systems", icon: ClipboardList, permission: { resource: "system_assets", action: "view" } },
      { label: "聚合拓扑", to: "/systems/topology", icon: Package, permission: { resource: "system_assets", action: "view" } },
      { label: "字段分类", to: "/system-field-categories", icon: ListTree, permission: { resource: "system_fields", action: "view" } }
    ]
  },
  {
    title: "盘点",
    icon: ClipboardList,
    items: [
      { label: "盘点任务", to: "/stocktakes", icon: ClipboardCheck, demo: true, permission: { resource: "stocktakes", action: "view" } },
      { label: "扫码工具", to: "/scan", icon: QrCode, demo: true, permission: { resource: "scan", action: "view" } }
    ]
  },
  {
    title: "系统",
    icon: Settings,
    items: [
      { label: "系统消息", to: "/notifications", icon: Bell, permission: { resource: "notifications", action: "view" } },
      { label: "部门管理", to: "/departments", icon: ListTree, permission: { resource: "departments", action: "view" } },
      { label: "人员管理", to: "/people", icon: UsersRound, permission: { resource: "people", action: "view" } },
      { label: "用户管理", to: "/users", icon: UserCog, permission: { resource: "users", action: "view" } },
      { label: "角色权限", to: "/roles", icon: Shield, permission: { resource: "roles", action: "view" } },
      { label: "数据源管理", to: "/dictionaries", icon: Database, permission: { resource: "dictionaries", action: "view" } },
      { label: "操作审计", to: "/logs", icon: FileSearch, demo: true, permission: { resource: "logs", action: "view" } },
      { label: "财务报表", to: "/reports", icon: FileBarChart, demo: true, permission: { resource: "reports", action: "view" } },
      { label: "系统设置", to: "/settings", icon: Settings, demo: true, permission: { resource: "settings", action: "view" } }
    ]
  }
];

const visibleMenuGroups = computed(() => {
  return menuGroups
    .map((group) => {
      const items = group.items.filter((item) => hasMenuPermission(item.permission));
      return { ...group, items };
    })
    .filter((group) => group.items.length);
});

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
  if (route.path.startsWith("/assets/office")) {
    return to === "/assets/office";
  }
  if (route.path.startsWith("/assets/datacenter")) {
    return to === "/assets/datacenter";
  }
  if (route.path.startsWith("/assets/import") || route.path.startsWith("/assets/flow")) {
    return route.path.startsWith(to);
  }
  if (route.path.startsWith("/assets/")) {
    if (to === "/assets/office" || to === "/assets/datacenter") {
      const scope = localStorage.getItem("assetDeptScope") || "";
      if (to === "/assets/datacenter") {
        return scope === "数据中心";
      }
      return scope !== "数据中心";
    }
    return false;
  }
  if (route.path.startsWith("/systems/topology")) {
    return to === "/systems/topology";
  }
  return route.path.startsWith(to);
};

const isGroupOpen = (title) => {
  if (openGroups.value.includes(title)) return true;
  const prefixes = groupRouteMap[title] || [];
  return prefixes.some((prefix) => {
    if (prefix === "/") {
      return route.path === "/";
    }
    return route.path.startsWith(prefix);
  });
};

const toggleGroup = (title) => {
  if (isGroupOpen(title)) {
    openGroups.value = [];
  } else {
    openGroups.value = [title];
  }
};

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
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

const groupRouteMap = {
  "总览": ["/"],
  "硬件资产管理": ["/assets", "/asset-types", "/maintenance", "/scrap"],
  "软件资产": ["/licenses", "/software-field-categories"],
  "系统资产管理": ["/systems", "/system-field-categories"],
  "盘点": ["/stocktakes", "/scan"],
  "系统": ["/notifications", "/departments", "/people", "/users", "/roles", "/logs", "/reports", "/settings"]
};

const ensureActiveGroupOpen = () => {
  const path = route.path;
  const match = visibleMenuGroups.value.find((group) => {
    const prefixes = groupRouteMap[group.title] || [];
    return prefixes.some((prefix) => {
      if (prefix === "/") {
        return path === "/";
      }
      return path.startsWith(prefix);
    });
  });
  if (!match) return;
  if (!openGroups.value.includes(match.title)) {
    openGroups.value = [match.title];
  }
};

const loadNotifications = async () => {
  if (!canViewNotifications.value) {
    notifications.value = [];
    notificationsLoading.value = false;
    return;
  }
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

watch(isSidebarCollapsed, (value) => {
  localStorage.setItem("assethub_sidebar_collapsed", value ? "1" : "0");
});

watch(openGroups, (value) => {
  localStorage.setItem("assethub_sidebar_open_groups", JSON.stringify(value));
});

watch(
  () => route.path,
  () => {
    ensureActiveGroupOpen();
  }
);

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
  document.documentElement.classList.add("theme-green");
  if (auth.token && !auth.permissionsLoaded) {
    auth.loadPermissions().catch(() => {});
  }
  if (!localStorage.getItem("roleCode") && auth.roleCode) {
    localStorage.setItem("roleCode", auth.roleCode);
  }
  const storedCollapsed = localStorage.getItem("assethub_sidebar_collapsed");
  if (storedCollapsed !== null) {
    isSidebarCollapsed.value = storedCollapsed === "1";
  }
  const storedGroups = localStorage.getItem("assethub_sidebar_open_groups");
  if (storedGroups) {
    try {
      openGroups.value = JSON.parse(storedGroups) || [];
    } catch {
      openGroups.value = [];
    }
  }
  ensureActiveGroupOpen();
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
  document.documentElement.classList.remove("theme-green");
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

.sidebar-link-sub {
  font-size: 12px !important;
  color: color-mix(in oklab, var(--foreground) 75%, transparent) !important;
}

.sidebar-link-text {
  font-size: 12px !important;
  color: color-mix(in oklab, var(--foreground) 75%, transparent) !important;
}

.sidebar-link-demo {
  color: color-mix(in oklab, var(--foreground) 45%, transparent) !important;
}

.sidebar-link-demo .sidebar-link-text {
  color: color-mix(in oklab, var(--foreground) 45%, transparent) !important;
}

.sidebar-demo-badge {
  margin-left: auto;
  border-radius: 999px;
  background: color-mix(in oklab, var(--primary) 18%, transparent);
  padding: 1px 5px;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: color-mix(in oklab, var(--primary) 70%, var(--foreground));
}

.sidebar-link-active {
  background: var(--accent);
  color: var(--accent-foreground);
}
</style>

