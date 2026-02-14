import axios from "axios";
import { useAuthStore } from "../stores/auth";
import router from "../router";

const api = axios.create({
  baseURL: "/api/v1"
});

api.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`;
  }
  return config;
});

let authRedirecting = false;

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      const auth = useAuthStore();
      if (auth.token) {
        auth.logout();
      }
      if (!authRedirecting) {
        authRedirecting = true;
        const target = "/login";
        if (router.currentRoute?.value?.path !== target) {
          router.replace(target).finally(() => {
            authRedirecting = false;
          });
        } else {
          authRedirecting = false;
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
