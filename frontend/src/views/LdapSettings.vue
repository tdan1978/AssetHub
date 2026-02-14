<template>
  <div class="space-y-6">
    <div class="rounded-lg border bg-background p-4">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-semibold">LDAP / AD 配置</h2>
          <p class="text-sm text-muted-foreground">配置 AD 连接信息后即可同步并支持域用户登录</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <Button variant="outline" @click="testConfig" :disabled="testing">
            {{ testing ? "测试中..." : "测试连接" }}
          </Button>
          <Button variant="outline" @click="syncUsers" :disabled="syncing">
            {{ syncing ? "同步中..." : "同步用户" }}
          </Button>
          <Button @click="saveConfig" :disabled="saving">
            {{ saving ? "保存中..." : "保存配置" }}
          </Button>
        </div>
      </div>
      <div v-if="message" class="mt-3 text-sm" :class="messageType === 'error' ? 'text-destructive' : 'text-green-600'">
        {{ message }}
      </div>
    </div>

    <div class="rounded-lg border bg-background p-4">
      <div class="form-grid-2">
        <div class="form-field">
          <label class="form-label">启用 LDAP</label>
          <div class="flex items-center gap-3">
            <Switch v-model="form.is_active" />
            <span class="text-sm text-muted-foreground">启用后允许同步</span>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label">允许 LDAP 登录</label>
          <div class="flex items-center gap-3">
            <Switch v-model="form.allow_login" />
            <span class="text-sm text-muted-foreground">允许域用户登录</span>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label">首次登录自动创建用户</label>
          <div class="flex items-center gap-3">
            <Switch v-model="form.auto_create" />
            <span class="text-sm text-muted-foreground">自动写入本地用户</span>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label">协议</label>
          <Select v-model="protocol">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择协议" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ldap">LDAP (389)</SelectItem>
              <SelectItem value="ldaps">LDAPS (636)</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="form-field">
          <label class="form-label">服务器地址</label>
          <Input v-model="form.host" placeholder="ad.example.com" />
        </div>
        <div class="form-field">
          <label class="form-label">端口</label>
          <Input v-model.number="form.port" type="number" />
        </div>
        <div class="form-field">
          <label class="form-label">Base DN</label>
          <Input v-model="form.base_dn" placeholder="DC=example,DC=com" />
        </div>
        <div class="form-field">
          <label class="form-label">Bind DN</label>
          <Input v-model="form.bind_dn" placeholder="CN=ldapreader,OU=IT,DC=example,DC=com" />
        </div>
        <div class="form-field">
          <label class="form-label">Bind 密码</label>
          <Input v-model="form.bind_password" type="password" placeholder="留空则保留原密码" />
        </div>
        <div class="form-field">
          <label class="form-label">StartTLS</label>
          <div class="flex items-center gap-3">
            <Switch v-model="form.use_starttls" />
            <span class="text-sm text-muted-foreground">仅用于 LDAP 协议</span>
          </div>
        </div>
        <div class="form-field">
          <label class="form-label">用户过滤器</label>
          <Textarea v-model="form.user_filter" placeholder="(&(objectClass=user)(!(objectClass=computer)))" />
        </div>
        <div class="form-field">
          <label class="form-label">用户名属性</label>
          <Input v-model="form.username_attr" placeholder="sAMAccountName" />
        </div>
        <div class="form-field">
          <label class="form-label">显示名属性</label>
          <Input v-model="form.display_name_attr" placeholder="displayName" />
        </div>
        <div class="form-field">
          <label class="form-label">邮箱属性</label>
          <Input v-model="form.email_attr" placeholder="mail" />
        </div>
        <div class="form-field">
          <label class="form-label">电话属性</label>
          <Input v-model="form.phone_attr" placeholder="mobile" />
        </div>
        <div class="form-field">
          <label class="form-label">部门属性</label>
          <Input v-model="form.dept_attr" placeholder="department" />
        </div>
        <div class="form-field">
          <label class="form-label">默认角色</label>
          <Select v-model="form.default_role_code">
            <SelectTrigger class="w-full">
              <SelectValue placeholder="选择默认角色" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="role in roles" :key="role.code" :value="role.code">
                {{ role.name }} ({{ role.code }})
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import api from "../api/client";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem
} from "../components/ui/select";

const form = ref({
  provider: "ad",
  is_active: false,
  host: "",
  port: 389,
  use_ssl: false,
  use_starttls: false,
  base_dn: "",
  bind_dn: "",
  bind_password: "",
  user_filter: "(&(objectClass=user)(!(objectClass=computer)))",
  username_attr: "sAMAccountName",
  display_name_attr: "displayName",
  email_attr: "mail",
  phone_attr: "mobile",
  dept_attr: "department",
  default_role_code: "employee",
  allow_login: true,
  auto_create: true
});

const roles = ref([]);
const saving = ref(false);
const testing = ref(false);
const syncing = ref(false);
const message = ref("");
const messageType = ref("ok");

const protocol = computed({
  get() {
    return form.value.use_ssl ? "ldaps" : "ldap";
  },
  set(value) {
    form.value.use_ssl = value === "ldaps";
    if (value === "ldaps" && form.value.port === 389) {
      form.value.port = 636;
    }
    if (value === "ldap" && form.value.port === 636) {
      form.value.port = 389;
    }
  }
});

const loadConfig = async () => {
  const { data } = await api.get("/ldap/config");
  form.value = {
    ...form.value,
    ...data,
    is_active: !!data?.is_active,
    allow_login: !!data?.allow_login,
    auto_create: !!data?.auto_create,
    use_ssl: !!data?.use_ssl,
    use_starttls: !!data?.use_starttls,
    bind_password: ""
  };
};

const loadRoles = async () => {
  const { data } = await api.get("/roles");
  roles.value = data || [];
};

const saveConfig = async () => {
  saving.value = true;
  message.value = "";
  try {
    const payload = {
      ...form.value,
      is_active: !!form.value.is_active,
      allow_login: !!form.value.allow_login,
      auto_create: !!form.value.auto_create,
      use_ssl: !!form.value.use_ssl,
      use_starttls: !!form.value.use_starttls
    };
    await api.put("/ldap/config", payload);
    messageType.value = "ok";
    message.value = "配置已保存";
    await loadConfig();
  } catch (err) {
    messageType.value = "error";
    message.value = err?.response?.data?.detail || "保存失败";
  } finally {
    saving.value = false;
  }
};

const testConfig = async () => {
  testing.value = true;
  message.value = "";
  try {
    const { data } = await api.post("/ldap/test");
    messageType.value = data.ok ? "ok" : "error";
    message.value = data.ok ? `连接成功，找到 ${data.users_found ?? 0} 个用户` : data.message;
  } catch (err) {
    messageType.value = "error";
    message.value = err?.response?.data?.detail || "测试失败";
  } finally {
    testing.value = false;
  }
};

const syncUsers = async () => {
  syncing.value = true;
  message.value = "";
  try {
    const { data } = await api.post("/ldap/sync");
    messageType.value = data.ok ? "ok" : "error";
    message.value = data.ok
      ? `同步完成：新增 ${data.created}，更新 ${data.updated}，跳过 ${data.skipped}`
      : "同步失败";
  } catch (err) {
    messageType.value = "error";
    message.value = err?.response?.data?.detail || "同步失败";
  } finally {
    syncing.value = false;
  }
};

onMounted(async () => {
  await loadRoles();
  await loadConfig();
});
</script>

<style scoped></style>



