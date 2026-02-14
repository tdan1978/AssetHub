import { createRouter, createWebHistory } from "vue-router";

const Dashboard = () => import("../views/Dashboard.vue");
const Assets = () => import("../views/Assets.vue");
const AssetCreate = () => import("../views/AssetCreate.vue");
const AssetEdit = () => import("../views/AssetEdit.vue");
const AssetImport = () => import("../views/AssetImport.vue");
const AssetFlow = () => import("../views/AssetFlow.vue");
const AssetTypes = () => import("../views/AssetTypes.vue");
const AssetTypeCreate = () => import("../views/AssetTypeCreate.vue");
const AssetTypeEdit = () => import("../views/AssetTypeEdit.vue");
const AssetFields = () => import("../views/AssetFields.vue");
const AssetFieldCreate = () => import("../views/AssetFieldCreate.vue");
const AssetFieldEdit = () => import("../views/AssetFieldEdit.vue");
const SystemAssets = () => import("../views/SystemAssets.vue");
const SystemTopologyOverview = () => import("../views/SystemTopologyOverview.vue");
const SystemAssetCreate = () => import("../views/SystemAssetCreate.vue");
const SystemAssetEdit = () => import("../views/SystemAssetEdit.vue");
const SystemFieldCategories = () => import("../views/SystemFieldCategories.vue");
const SystemFieldCategoryCreate = () => import("../views/SystemFieldCategoryCreate.vue");
const SystemFieldCategoryEdit = () => import("../views/SystemFieldCategoryEdit.vue");
const SystemFields = () => import("../views/SystemFields.vue");
const SystemFieldCreate = () => import("../views/SystemFieldCreate.vue");
const SystemFieldEdit = () => import("../views/SystemFieldEdit.vue");
const Maintenance = () => import("../views/Maintenance.vue");
const RepairCreate = () => import("../views/RepairCreate.vue");
const RepairEdit = () => import("../views/RepairEdit.vue");
const MaintenanceInfo = () => import("../views/MaintenanceInfo.vue");
const Scrap = () => import("../views/Scrap.vue");
const Licenses = () => import("../views/Licenses.vue");
const LicenseCreate = () => import("../views/LicenseCreate.vue");
const LicenseEdit = () => import("../views/LicenseEdit.vue");
const SoftwareFieldCategories = () => import("../views/SoftwareFieldCategories.vue");
const SoftwareFieldCategoryCreate = () => import("../views/SoftwareFieldCategoryCreate.vue");
const SoftwareFieldCategoryEdit = () => import("../views/SoftwareFieldCategoryEdit.vue");
const SoftwareFields = () => import("../views/SoftwareFields.vue");
const SoftwareFieldCreate = () => import("../views/SoftwareFieldCreate.vue");
const SoftwareFieldEdit = () => import("../views/SoftwareFieldEdit.vue");
const Stocktakes = () => import("../views/Stocktakes.vue");
const StocktakeCreate = () => import("../views/StocktakeCreate.vue");
const StocktakeEdit = () => import("../views/StocktakeEdit.vue");
const Scan = () => import("../views/Scan.vue");
const Users = () => import("../views/Users.vue");
const UserCreate = () => import("../views/UserCreate.vue");
const UserEdit = () => import("../views/UserEdit.vue");
const LdapSettings = () => import("../views/LdapSettings.vue");
const Departments = () => import("../views/Departments.vue");
const DepartmentCreate = () => import("../views/DepartmentCreate.vue");
const DepartmentEdit = () => import("../views/DepartmentEdit.vue");
const People = () => import("../views/People.vue");
const PersonCreate = () => import("../views/PersonCreate.vue");
const PersonEdit = () => import("../views/PersonEdit.vue");
const Roles = () => import("../views/Roles.vue");
const RoleCreate = () => import("../views/RoleCreate.vue");
const RoleEdit = () => import("../views/RoleEdit.vue");
const Logs = () => import("../views/Logs.vue");
const Reports = () => import("../views/Reports.vue");
const Settings = () => import("../views/Settings.vue");
const Notifications = () => import("../views/Notifications.vue");
const Dictionaries = () => import("../views/Dictionaries.vue");
const DictionaryCreate = () => import("../views/DictionaryCreate.vue");
const DictionaryEdit = () => import("../views/DictionaryEdit.vue");
const Login = () => import("../views/Login.vue");

const routes = [
  { path: "/", component: Dashboard },
  { path: "/assets", redirect: "/assets/office" },
  { path: "/assets/office", component: Assets },
  { path: "/assets/datacenter", component: Assets },
  { path: "/assets/new", component: AssetCreate },
  { path: "/assets/:id/edit", component: AssetEdit },
  { path: "/asset-types", component: AssetTypes },
  { path: "/asset-types/new", component: AssetTypeCreate },
  { path: "/asset-types/:id/edit", component: AssetTypeEdit },
  { path: "/asset-types/:id/fields", component: AssetFields },
  { path: "/asset-types/:id/fields/new", component: AssetFieldCreate },
  { path: "/asset-types/:id/fields/:fieldId/edit", component: AssetFieldEdit },
  { path: "/systems", component: SystemAssets },
  { path: "/systems/topology", component: SystemTopologyOverview },
  { path: "/systems/new", component: SystemAssetCreate },
  { path: "/systems/:id/edit", component: SystemAssetEdit },
  { path: "/system-field-categories", component: SystemFieldCategories },
  { path: "/system-field-categories/new", component: SystemFieldCategoryCreate },
  { path: "/system-field-categories/:id/edit", component: SystemFieldCategoryEdit },
  { path: "/system-field-categories/:id/fields", component: SystemFields },
  { path: "/system-field-categories/:id/fields/new", component: SystemFieldCreate },
  { path: "/system-field-categories/:id/fields/:fieldId/edit", component: SystemFieldEdit },
  { path: "/assets/import", component: AssetImport },
  { path: "/assets/flow", component: AssetFlow },
  { path: "/maintenance", component: Maintenance },
  { path: "/maintenance/repairs/new", component: RepairCreate },
  { path: "/maintenance/repairs/:id/edit", component: RepairEdit },
  { path: "/maintenance/info", component: MaintenanceInfo },
  { path: "/scrap", component: Scrap },
  { path: "/licenses", component: Licenses },
  { path: "/licenses/new", component: LicenseCreate },
  { path: "/licenses/:id/edit", component: LicenseEdit },
  { path: "/software-field-categories", component: SoftwareFieldCategories },
  { path: "/software-field-categories/new", component: SoftwareFieldCategoryCreate },
  { path: "/software-field-categories/:id/edit", component: SoftwareFieldCategoryEdit },
  { path: "/software-field-categories/:id/fields", component: SoftwareFields },
  { path: "/software-field-categories/:id/fields/new", component: SoftwareFieldCreate },
  { path: "/software-field-categories/:id/fields/:fieldId/edit", component: SoftwareFieldEdit },
  { path: "/stocktakes", component: Stocktakes },
  { path: "/stocktakes/new", component: StocktakeCreate },
  { path: "/stocktakes/:id/edit", component: StocktakeEdit },
  { path: "/scan", component: Scan },
  { path: "/users", component: Users },
  { path: "/users/ldap", component: LdapSettings },
  { path: "/users/new", component: UserCreate },
  { path: "/users/:id/edit", component: UserEdit },
  { path: "/departments", component: Departments },
  { path: "/departments/new", component: DepartmentCreate },
  { path: "/departments/:id/edit", component: DepartmentEdit },
  { path: "/people", component: People },
  { path: "/people/new", component: PersonCreate },
  { path: "/people/:id/edit", component: PersonEdit },
  { path: "/roles", component: Roles },
  { path: "/roles/new", component: RoleCreate },
  { path: "/roles/:id/edit", component: RoleEdit },
  { path: "/logs", component: Logs },
  { path: "/reports", component: Reports },
  { path: "/settings", component: Settings },
  { path: "/dictionaries", component: Dictionaries },
  { path: "/dictionaries/new", component: DictionaryCreate },
  { path: "/dictionaries/:id/edit", component: DictionaryEdit },
  { path: "/notifications", component: Notifications },
  { path: "/login", component: Login }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

const hasPermission = (resource, action = "view") => {
  const roleCode = localStorage.getItem("roleCode") || "";
  if (roleCode === "super_admin") return true;
  const raw = localStorage.getItem("assethub_permissions");
  if (!raw) return true;
  try {
    const perms = JSON.parse(raw);
    return perms.includes(`${resource}:${action}`);
  } catch {
    return false;
  }
};
const hasAnyPermission = (items = []) => items.some((item) => hasPermission(item.resource, item.action || "view"));

const routePermission = (path) => {
  if (path === "/") return { resource: "dashboard", action: "view" };
  if (path === "/assets") {
    return {
      any: [
        { resource: "office_hardware_assets", action: "view" },
        { resource: "datacenter_hardware_assets", action: "view" }
      ]
    };
  }
  if (path.startsWith("/assets/office")) return { resource: "office_hardware_assets", action: "view" };
  if (path.startsWith("/assets/datacenter")) return { resource: "datacenter_hardware_assets", action: "view" };
  if (path === "/assets/new") {
    return {
      any: [
        { resource: "office_hardware_assets", action: "create" },
        { resource: "datacenter_hardware_assets", action: "create" }
      ]
    };
  }
  if (path.startsWith("/assets/") && path.endsWith("/edit")) {
    return {
      any: [
        { resource: "office_hardware_assets", action: "update" },
        { resource: "datacenter_hardware_assets", action: "update" }
      ]
    };
  }
  if (path.startsWith("/asset-types/") && path.includes("/fields/") && path.endsWith("/edit")) {
    return { resource: "asset_types", action: "update" };
  }
  if (path.startsWith("/asset-types/") && path.endsWith("/fields/new")) {
    return { resource: "asset_types", action: "create" };
  }
  if (path.startsWith("/asset-types/") && path.endsWith("/edit")) return { resource: "asset_types", action: "update" };
  if (path === "/asset-types/new") return { resource: "asset_types", action: "create" };
  if (path.startsWith("/asset-types/") && path.includes("/fields")) return { resource: "asset_types", action: "view" };
  if (path.startsWith("/asset-types")) return { resource: "asset_types", action: "view" };
  if (path === "/assets/import") {
    return {
      any: [
        { resource: "office_hardware_assets", action: "create" },
        { resource: "datacenter_hardware_assets", action: "create" }
      ]
    };
  }
  if (path === "/assets/flow") {
    return {
      any: [
        { resource: "office_hardware_assets", action: "update" },
        { resource: "datacenter_hardware_assets", action: "update" }
      ]
    };
  }
  if (path.startsWith("/maintenance")) {
    if (path.endsWith("/new")) return { resource: "maintenance", action: "create" };
    if (path.endsWith("/edit")) return { resource: "maintenance", action: "update" };
    return { resource: "maintenance", action: "view" };
  }
  if (path.startsWith("/scrap")) return { resource: "scrap", action: "view" };
  if (path.startsWith("/licenses")) {
    if (path === "/licenses/new") return { resource: "software_assets", action: "create" };
    if (path.endsWith("/edit")) return { resource: "software_assets", action: "update" };
    return { resource: "software_assets", action: "view" };
  }
  if (path.startsWith("/software-field-categories/") && path.includes("/fields/") && path.endsWith("/edit")) {
    return { resource: "software_fields", action: "update" };
  }
  if (path.startsWith("/software-field-categories/") && path.endsWith("/fields/new")) {
    return { resource: "software_fields", action: "create" };
  }
  if (path.startsWith("/software-field-categories/") && path.endsWith("/edit")) {
    return { resource: "software_fields", action: "update" };
  }
  if (path === "/software-field-categories/new") return { resource: "software_fields", action: "create" };
  if (path.startsWith("/software-field-categories/") && path.includes("/fields")) {
    return { resource: "software_fields", action: "view" };
  }
  if (path.startsWith("/software-field-categories")) return { resource: "software_fields", action: "view" };
  if (path.startsWith("/systems")) {
    if (path === "/systems/new") return { resource: "system_assets", action: "create" };
    if (path.endsWith("/edit")) return { resource: "system_assets", action: "update" };
    return { resource: "system_assets", action: "view" };
  }
  if (path.startsWith("/system-field-categories/") && path.includes("/fields/") && path.endsWith("/edit")) {
    return { resource: "system_fields", action: "update" };
  }
  if (path.startsWith("/system-field-categories/") && path.endsWith("/fields/new")) {
    return { resource: "system_fields", action: "create" };
  }
  if (path.startsWith("/system-field-categories/") && path.endsWith("/edit")) {
    return { resource: "system_fields", action: "update" };
  }
  if (path === "/system-field-categories/new") return { resource: "system_fields", action: "create" };
  if (path.startsWith("/system-field-categories/") && path.includes("/fields")) {
    return { resource: "system_fields", action: "view" };
  }
  if (path.startsWith("/system-field-categories")) return { resource: "system_fields", action: "view" };
  if (path.startsWith("/stocktakes")) {
    if (path === "/stocktakes/new") return { resource: "stocktakes", action: "create" };
    if (path.endsWith("/edit")) return { resource: "stocktakes", action: "update" };
    return { resource: "stocktakes", action: "view" };
  }
  if (path.startsWith("/scan")) return { resource: "scan", action: "view" };
  if (path.startsWith("/departments")) {
    if (path === "/departments/new") return { resource: "departments", action: "create" };
    if (path.endsWith("/edit")) return { resource: "departments", action: "update" };
    return { resource: "departments", action: "view" };
  }
  if (path.startsWith("/people")) {
    if (path === "/people/new") return { resource: "people", action: "create" };
    if (path.endsWith("/edit")) return { resource: "people", action: "update" };
    return { resource: "people", action: "view" };
  }
  if (path.startsWith("/users")) {
    if (path === "/users/new") return { resource: "users", action: "create" };
    if (path.endsWith("/edit")) return { resource: "users", action: "update" };
    return { resource: "users", action: "view" };
  }
  if (path.startsWith("/roles")) return { resource: "roles", action: "view" };
  if (path.startsWith("/notifications")) return { resource: "notifications", action: "view" };
  if (path.startsWith("/logs")) return { resource: "logs", action: "view" };
  if (path.startsWith("/reports")) return { resource: "reports", action: "view" };
  if (path.startsWith("/settings")) return { resource: "settings", action: "view" };
  if (path.startsWith("/dictionaries")) return { resource: "dictionaries", action: "view" };
  return null;
};

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (to.path !== "/login" && !token) {
    return "/login";
  }
  if (to.path === "/login" && token) {
    return "/";
  }
  if (to.path !== "/login") {
    const needed = routePermission(to.path);
    if (needed) {
      const allowed = needed.any ? hasAnyPermission(needed.any) : hasPermission(needed.resource, needed.action);
      if (!allowed) {
        return "/";
      }
    }
  }
  if (to.path === "/assets") {
    const scope = localStorage.getItem("assetDeptScope");
    if (scope === "数据中心") {
      return "/assets/datacenter";
    }
    return "/assets/office";
  }
});

export default router;

