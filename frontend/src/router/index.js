import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Assets from "../views/Assets.vue";
import AssetImport from "../views/AssetImport.vue";
import AssetFlow from "../views/AssetFlow.vue";
import AssetTypes from "../views/AssetTypes.vue";
import Maintenance from "../views/Maintenance.vue";
import Scrap from "../views/Scrap.vue";
import Licenses from "../views/Licenses.vue";
import Stocktakes from "../views/Stocktakes.vue";
import Scan from "../views/Scan.vue";
import Users from "../views/Users.vue";
import Roles from "../views/Roles.vue";
import Logs from "../views/Logs.vue";
import Reports from "../views/Reports.vue";
import Settings from "../views/Settings.vue";
import Login from "../views/Login.vue";

const routes = [
  { path: "/", component: Dashboard },
  { path: "/assets", component: Assets },
  { path: "/asset-types", component: AssetTypes },
  { path: "/assets/import", component: AssetImport },
  { path: "/assets/flow", component: AssetFlow },
  { path: "/maintenance", component: Maintenance },
  { path: "/scrap", component: Scrap },
  { path: "/licenses", component: Licenses },
  { path: "/stocktakes", component: Stocktakes },
  { path: "/scan", component: Scan },
  { path: "/users", component: Users },
  { path: "/roles", component: Roles },
  { path: "/logs", component: Logs },
  { path: "/reports", component: Reports },
  { path: "/settings", component: Settings },
  { path: "/login", component: Login }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (to.path !== "/login" && !token) {
    return "/login";
  }
  if (to.path === "/login" && token) {
    return "/";
  }
});

export default router;
