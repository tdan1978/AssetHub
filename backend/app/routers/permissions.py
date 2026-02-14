from fastapi import APIRouter, Depends

from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])

RESOURCES = [
    {"key": "dashboard", "label": "仪表盘", "actions": ["view", "edit", "publish"]},
    {"key": "office_hardware_assets", "label": "办公硬件", "actions": ["view", "create", "update", "delete"]},
    {"key": "datacenter_hardware_assets", "label": "数据中心硬件", "actions": ["view", "create", "update", "delete"]},
    {"key": "asset_types", "label": "资产类型/字段", "actions": ["view", "create", "update", "delete"]},
    {"key": "maintenance", "label": "维保与报修", "actions": ["view", "create", "update"]},
    {"key": "scrap", "label": "报废管理", "actions": ["view", "update"]},
    {"key": "software_assets", "label": "软件资产", "actions": ["view", "create", "update", "delete"]},
    {"key": "software_fields", "label": "软件字段配置", "actions": ["view", "create", "update", "delete"]},
    {"key": "system_assets", "label": "系统资产", "actions": ["view", "create", "update", "delete"], "scopes": ["own", "all"]},
    {"key": "system_fields", "label": "系统字段配置", "actions": ["view", "create", "update", "delete"]},
    {"key": "stocktakes", "label": "盘点", "actions": ["view", "create", "update"]},
    {"key": "scan", "label": "扫码工具", "actions": ["view"]},
    {"key": "departments", "label": "部门管理", "actions": ["view", "create", "update", "delete"]},
    {"key": "people", "label": "人员管理", "actions": ["view", "create", "update", "delete"]},
    {"key": "users", "label": "用户管理", "actions": ["view", "create", "update", "delete"]},
    {"key": "roles", "label": "角色权限", "actions": ["view", "update"]},
    {"key": "dictionaries", "label": "数据源管理", "actions": ["view", "create", "update", "delete"]},
    {"key": "notifications", "label": "系统消息", "actions": ["view"]},
    {"key": "logs", "label": "操作审计", "actions": ["view"]},
    {"key": "reports", "label": "财务报表", "actions": ["view"]},
    {"key": "settings", "label": "系统设置", "actions": ["view", "update"]},
]


@router.get("/resources")
def list_resources(_: object = Depends(get_current_user)):
    return RESOURCES
