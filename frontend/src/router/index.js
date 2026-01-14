import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Assets from "../views/Assets.vue";
import AssetCreate from "../views/AssetCreate.vue";
import AssetEdit from "../views/AssetEdit.vue";
import AssetImport from "../views/AssetImport.vue";
import AssetFlow from "../views/AssetFlow.vue";
import AssetTypes from "../views/AssetTypes.vue";
import AssetTypeCreate from "../views/AssetTypeCreate.vue";
import AssetTypeEdit from "../views/AssetTypeEdit.vue";
import AssetFields from "../views/AssetFields.vue";
import AssetFieldCreate from "../views/AssetFieldCreate.vue";
import AssetFieldEdit from "../views/AssetFieldEdit.vue";
import SystemAssets from "../views/SystemAssets.vue";
import SystemAssetCreate from "../views/SystemAssetCreate.vue";
import SystemAssetEdit from "../views/SystemAssetEdit.vue";
import SystemFieldCategories from "../views/SystemFieldCategories.vue";
import SystemFieldCategoryCreate from "../views/SystemFieldCategoryCreate.vue";
import SystemFieldCategoryEdit from "../views/SystemFieldCategoryEdit.vue";
import SystemFields from "../views/SystemFields.vue";
import SystemFieldCreate from "../views/SystemFieldCreate.vue";
import SystemFieldEdit from "../views/SystemFieldEdit.vue";
import Maintenance from "../views/Maintenance.vue";
import RepairCreate from "../views/RepairCreate.vue";
import RepairEdit from "../views/RepairEdit.vue";
import MaintenanceInfo from "../views/MaintenanceInfo.vue";
import Scrap from "../views/Scrap.vue";
import Licenses from "../views/Licenses.vue";
import LicenseCreate from "../views/LicenseCreate.vue";
import LicenseEdit from "../views/LicenseEdit.vue";
import SoftwareFieldCategories from "../views/SoftwareFieldCategories.vue";
import SoftwareFieldCategoryCreate from "../views/SoftwareFieldCategoryCreate.vue";
import SoftwareFieldCategoryEdit from "../views/SoftwareFieldCategoryEdit.vue";
import SoftwareFields from "../views/SoftwareFields.vue";
import SoftwareFieldCreate from "../views/SoftwareFieldCreate.vue";
import SoftwareFieldEdit from "../views/SoftwareFieldEdit.vue";
import Stocktakes from "../views/Stocktakes.vue";
import StocktakeCreate from "../views/StocktakeCreate.vue";
import StocktakeEdit from "../views/StocktakeEdit.vue";
import Scan from "../views/Scan.vue";
import Users from "../views/Users.vue";
import UserCreate from "../views/UserCreate.vue";
import UserEdit from "../views/UserEdit.vue";
import Roles from "../views/Roles.vue";
import Logs from "../views/Logs.vue";
import Reports from "../views/Reports.vue";
import Settings from "../views/Settings.vue";
import Notifications from "../views/Notifications.vue";
import Login from "../views/Login.vue";

const routes = [
  { path: "/", component: Dashboard },
  { path: "/assets", component: Assets },
  { path: "/assets/new", component: AssetCreate },
  { path: "/assets/:id/edit", component: AssetEdit },
  { path: "/asset-types", component: AssetTypes },
  { path: "/asset-types/new", component: AssetTypeCreate },
  { path: "/asset-types/:id/edit", component: AssetTypeEdit },
  { path: "/asset-types/:id/fields", component: AssetFields },
  { path: "/asset-types/:id/fields/new", component: AssetFieldCreate },
  { path: "/asset-types/:id/fields/:fieldId/edit", component: AssetFieldEdit },
  { path: "/systems", component: SystemAssets },
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
  { path: "/users/new", component: UserCreate },
  { path: "/users/:id/edit", component: UserEdit },
  { path: "/roles", component: Roles },
  { path: "/logs", component: Logs },
  { path: "/reports", component: Reports },
  { path: "/settings", component: Settings },
  { path: "/notifications", component: Notifications },
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
