import { defineStore } from "pinia";
import api from "../api/client";

const decodeRoleCode = (token) => {
  if (!token) return "";
  const parts = token.split(".");
  if (parts.length < 2) return "";
  try {
    const payload = JSON.parse(atob(parts[1]));
    if (payload.role_codes && Array.isArray(payload.role_codes)) {
      return payload.role_codes.includes("super_admin") ? "super_admin" : (payload.role_code || payload.role_codes[0] || "");
    }
    return payload.role_code || "";
  } catch {
    return "";
  }
};

export const useAuthStore = defineStore("auth", {
  state: () => {
    const token = localStorage.getItem("token") || "";
    const storedRole = localStorage.getItem("roleCode") || "";
    const storedPermissions = localStorage.getItem("assethub_permissions");
    return {
      token,
      username: localStorage.getItem("username") || "",
      fullName: localStorage.getItem("fullName") || "",
      roleCode: storedRole || decodeRoleCode(token),
      permissions: storedPermissions ? JSON.parse(storedPermissions) : [],
      permissionsLoaded: !!storedPermissions
    };
  },
  actions: {
    async login(username, password) {
      const form = new FormData();
      form.append("username", username);
      form.append("password", password);
      const { data } = await api.post("/auth/login", form);
      this.token = data.access_token;
      this.username = data.username || username;
      this.fullName = data.full_name || "";
      this.roleCode = decodeRoleCode(data.access_token);
      localStorage.setItem("token", this.token);
      localStorage.setItem("username", this.username);
      localStorage.setItem("fullName", this.fullName);
      localStorage.setItem("roleCode", this.roleCode);
      await this.loadPermissions();
    },
    async loadPermissions() {
      if (!this.token) return;
      const { data } = await api.get("/roles/me/permissions");
      this.permissions = data.map((item) => `${item.resource}:${item.action}`);
      this.permissionsLoaded = true;
      localStorage.setItem("assethub_permissions", JSON.stringify(this.permissions));
    },
    logout() {
      this.token = "";
      this.username = "";
      this.fullName = "";
      this.roleCode = "";
      this.permissions = [];
      this.permissionsLoaded = false;
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      localStorage.removeItem("fullName");
      localStorage.removeItem("roleCode");
      localStorage.removeItem("assethub_permissions");
    }
  }
});
