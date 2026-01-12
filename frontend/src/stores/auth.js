import { defineStore } from "pinia";
import api from "../api/client";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || "",
    username: localStorage.getItem("username") || ""
  }),
  actions: {
    async login(username, password) {
      const form = new FormData();
      form.append("username", username);
      form.append("password", password);
      const { data } = await api.post("/auth/login", form);
      this.token = data.access_token;
      this.username = username;
      localStorage.setItem("token", this.token);
      localStorage.setItem("username", this.username);
    },
    logout() {
      this.token = "";
      this.username = "";
      localStorage.removeItem("token");
      localStorage.removeItem("username");
    }
  }
});
