from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, engine, SessionLocal
from app.models.category import Category
from app.models.category_field import CategoryField
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.system_field_category import SystemFieldCategory
from app.models.system_field import SystemField
from app.models.system_app import SystemApp
from app.models.system_field_value import SystemFieldValue
from app.models.software_field_category import SoftwareFieldCategory
from app.models.software_field import SoftwareField
from app.models.department import Department
from app.models.person import Person
from app.models.dict_type import DictType
from app.models.dict_item import DictItem
from app.models.dashboard_template import DashboardTemplate
from app.models.dashboard_widget import DashboardWidget
from app.routers import auth, assets, asset_fields, licenses, users, roles, stocktakes, dashboard, categories, maintenance, systems, system_fields, system_field_categories, software_field_categories, license_fields, notifications, departments, people, permissions, dictionaries, ldap

app = FastAPI(title="AssetHub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "AssetHub API"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(assets.router)
app.include_router(asset_fields.router)
app.include_router(licenses.router)
app.include_router(maintenance.router)
app.include_router(stocktakes.router)
app.include_router(dashboard.router)
app.include_router(categories.router)
app.include_router(systems.router)
app.include_router(system_fields.router)
app.include_router(system_field_categories.router)
app.include_router(software_field_categories.router)
app.include_router(license_fields.router)
app.include_router(notifications.router)
app.include_router(departments.router)
app.include_router(people.router)
app.include_router(permissions.router)
app.include_router(dictionaries.router)
app.include_router(ldap.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'dict_types' "
                "AND COLUMN_NAME = 'scope'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE dict_types ADD COLUMN scope VARCHAR(20) NOT NULL DEFAULT 'global'"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'assets' "
                "AND COLUMN_NAME = 'category_id'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE assets ADD COLUMN category_id INT NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'categories' "
                "AND COLUMN_NAME = 'usage_scope'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE categories ADD COLUMN usage_scope VARCHAR(20) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'users' "
                "AND COLUMN_NAME = 'asset_scope'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE users ADD COLUMN asset_scope VARCHAR(20) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'users' "
                "AND COLUMN_NAME = 'phone'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(50) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'users' "
                "AND COLUMN_NAME = 'wecom_name'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE users ADD COLUMN wecom_name VARCHAR(100) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'category_id'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN category_id INT NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'visibility_rules'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN visibility_rules JSON NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'reminder_enabled'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN reminder_enabled BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'reminder_days'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN reminder_days INT NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'repeatable'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN repeatable BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'is_locked'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN is_locked BOOLEAN DEFAULT 0"))
        connection.execute(text("UPDATE category_fields SET is_locked = 0 WHERE is_locked = 1"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'usage_scope'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN usage_scope VARCHAR(20) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'visibility_rules'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN visibility_rules JSON NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'reminder_enabled'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN reminder_enabled BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'reminder_days'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN reminder_days INT NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'repeatable'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN repeatable BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'data_source'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN data_source VARCHAR(50) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'software_fields' "
                "AND COLUMN_NAME = 'visibility_rules'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE software_fields ADD COLUMN visibility_rules JSON NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'software_fields' "
                "AND COLUMN_NAME = 'reminder_enabled'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE software_fields ADD COLUMN reminder_enabled BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'software_fields' "
                "AND COLUMN_NAME = 'reminder_days'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE software_fields ADD COLUMN reminder_days INT NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'data_source'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN data_source VARCHAR(50) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'searchable'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN searchable BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'category_fields' "
                "AND COLUMN_NAME = 'multi_select_mode'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE category_fields ADD COLUMN multi_select_mode VARCHAR(20) NULL"))
        connection.execute(
            text(
                "UPDATE category_fields "
                "SET field_type = 'single_select', searchable = 1 "
                "WHERE field_type = 'combo_select'"
            )
        )
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'software_fields' "
                "AND COLUMN_NAME = 'data_source'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE software_fields ADD COLUMN data_source VARCHAR(50) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'software_fields' "
                "AND COLUMN_NAME = 'searchable'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE software_fields ADD COLUMN searchable BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'software_fields' "
                "AND COLUMN_NAME = 'multi_select_mode'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE software_fields ADD COLUMN multi_select_mode VARCHAR(20) NULL"))
        connection.execute(
            text(
                "UPDATE software_fields "
                "SET field_type = 'single_select', searchable = 1 "
                "WHERE field_type = 'combo_select'"
            )
        )
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'searchable'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN searchable BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'multi_select_mode'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN multi_select_mode VARCHAR(20) NULL"))
        connection.execute(
            text(
                "UPDATE system_fields "
                "SET field_type = 'single_select', searchable = 1 "
                "WHERE field_type = 'combo_select'"
            )
        )
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_fields' "
                "AND COLUMN_NAME = 'is_builtin'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_fields ADD COLUMN is_builtin BOOLEAN DEFAULT 0"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'role_permissions' "
                "AND COLUMN_NAME = 'scope'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE role_permissions ADD COLUMN scope VARCHAR(20) NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'roles' "
                "AND COLUMN_NAME = 'is_active'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE roles ADD COLUMN is_active BOOLEAN DEFAULT 1"))
        connection.execute(text("UPDATE roles SET is_active = 1 WHERE is_active IS NULL"))
        result = connection.execute(
            text(
                "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'system_apps' "
                "AND COLUMN_NAME = 'ops_owner_b'"
            )
        )
        if result.scalar() == 0:
            connection.execute(text("ALTER TABLE system_apps ADD COLUMN ops_owner_b VARCHAR(100) NULL"))
        connection.execute(
            text("ALTER TABLE system_apps MODIFY COLUMN app_name VARCHAR(200) NULL")
        )
        connection.execute(
            text("ALTER TABLE system_apps MODIFY COLUMN app_code VARCHAR(100) NULL")
        )
        license_columns = [
            ("version", "VARCHAR(50) NULL"),
            ("vendor", "VARCHAR(100) NULL"),
            ("category", "VARCHAR(100) NULL"),
            ("vendor_url", "VARCHAR(255) NULL"),
            ("license_type", "VARCHAR(50) NULL"),
            ("billing_mode", "VARCHAR(50) NULL"),
            ("activation_limit", "VARCHAR(50) NULL"),
            ("expiry_type", "VARCHAR(50) NULL"),
            ("renewal_at", "DATE NULL"),
            ("compliance_status", "VARCHAR(50) NULL"),
            ("cost", "DECIMAL(12,2) NULL"),
            ("purchase_date", "DATE NULL"),
            ("order_no", "VARCHAR(100) NULL"),
            ("supplier", "VARCHAR(100) NULL"),
        ]
        for column, definition in license_columns:
            result = connection.execute(
                text(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() "
                    "AND TABLE_NAME = 'licenses' "
                    "AND COLUMN_NAME = :col"
                ),
                {"col": column},
            )
            if result.scalar() == 0:
                connection.execute(text(f"ALTER TABLE licenses ADD COLUMN {column} {definition}"))
        connection.execute(text("ALTER TABLE licenses MODIFY COLUMN name VARCHAR(100) NULL"))
        connection.execute(text("ALTER TABLE licenses MODIFY COLUMN license_key TEXT NULL"))
        connection.execute(text("ALTER TABLE licenses MODIFY COLUMN total_qty INT NULL"))

    seed_system_field_categories()
    migrate_system_legacy_fields_to_custom_values()
    seed_software_field_categories()
    seed_office_asset_fields()
    seed_datacenter_asset_fields()
    seed_dashboard_templates()
    seed_dashboard_permissions()
    migrate_user_roles()
    cleanup_deleted_categories()


def seed_system_field_categories():
    db = SessionLocal()
    try:
        categories = [
            ("基础字段", "base", 1),
            ("技术栈与环境", "tech", 2),
            ("管理与运维", "ops", 3),
            ("自定义字段", "custom", 99),
        ]
        category_map = {}
        for name, code, order in categories:
            item = (
                db.query(SystemFieldCategory)
                .filter(SystemFieldCategory.code == code)
                .first()
            )
            if not item:
                item = (
                    db.query(SystemFieldCategory)
                    .filter(SystemFieldCategory.name == name)
                    .first()
                )
            if not item:
                item = SystemFieldCategory(
                    name=name,
                    code=code,
                    sort_order=order,
                    is_active=True,
                    is_deleted=False,
                )
                db.add(item)
            else:
                if item.is_deleted:
                    item.is_deleted = False
                if not item.is_active:
                    item.is_active = True
                item.code = code
                item.name = name
                item.sort_order = order
            db.commit()
            db.refresh(item)
            category_map[name] = item.id

        base_fields = [
            ("系统名称", "app_name", "text", "基础字段", True, None, 1, True),
            ("系统编码", "app_code", "text", "基础字段", True, None, 2, True),
            ("系统状态", "app_status", "single_select", "基础字段", False, ["开发中", "测试中", "运行中", "维护中", "已下线"], 3, True),
            ("业务负责人", "biz_owner", "text", "管理与运维", False, None, 1, True),
            ("技术负责人", "tech_owner", "text", "管理与运维", False, None, 2, True),
            ("运维负责人", "ops_owner", "single_select", "管理与运维", False, None, 3, True),
            ("运维负责人B", "ops_owner_b", "single_select", "管理与运维", False, None, 4, True),
            ("访问地址 (URL)", "access_url", "text", "基础字段", False, None, 4, False),
            ("系统分类", "app_category", "single_select", "基础字段", False, ["业务系统", "工具系统", "中间件", "内部平台"], 5, False),
            ("架构类型", "arch_type", "single_select", "技术栈与环境", False, ["B/S", "C/S", "微服务", "单体架构"], 1, False),
            ("开发语言", "dev_lang", "single_select", "技术栈与环境", False, ["Python", "Java", "Go", "PHP"], 2, False),
            ("数据库", "db_type", "single_select", "技术栈与环境", False, ["MySQL", "PostgreSQL", "Oracle", "Redis"], 3, False),
            ("部署方式", "deploy_type", "single_select", "技术栈与环境", False, ["物理机部署", "虚拟机部署", "容器化 (K8s)"], 4, False),
            ("源代码地址", "repo_url", "text", "技术栈与环境", False, None, 5, False),
            ("等级保护级别", "sec_level", "single_select", "管理与运维", False, ["等保一级", "等保二级", "等保三级"], 5, False),
        ]

        for name, key, ftype, cat_name, required, options, order, builtin in base_fields:
            field = (
                db.query(SystemField)
                .filter(SystemField.field_key == key, SystemField.is_deleted == False)
                .first()
            )
            if not field:
                field = SystemField(
                    name=name,
                    field_key=key,
                    field_type=ftype,
                    is_required=required,
                    options=options,
                    sort_order=order,
                    category_id=category_map.get(cat_name),
                    is_builtin=builtin,
                )
                if key in ("ops_owner", "ops_owner_b"):
                    field.data_source = "users"
                    field.searchable = True
                db.add(field)
            else:
                field.name = name
                field.field_type = ftype
                field.is_required = required
                field.sort_order = order
                field.category_id = category_map.get(cat_name)
                field.is_builtin = builtin
                if key in ("ops_owner", "ops_owner_b"):
                    field.data_source = "users"
                    field.searchable = True
                if options is not None:
                    field.options = options
            db.commit()

        db.query(SystemField).filter(SystemField.category_id == None).update(
            {"category_id": category_map.get("自定义字段")}
        )
        db.commit()
    finally:
        db.close()


def migrate_system_legacy_fields_to_custom_values():
    db = SessionLocal()
    try:
        legacy_keys = [
            "access_url",
            "app_category",
            "arch_type",
            "dev_lang",
            "db_type",
            "deploy_type",
            "repo_url",
            "sec_level",
        ]
        fields = (
            db.query(SystemField)
            .filter(SystemField.field_key.in_(legacy_keys), SystemField.is_deleted == False)
            .all()
        )
        if not fields:
            return
        field_map = {item.field_key: item for item in fields}
        systems_list = db.query(SystemApp).filter(SystemApp.is_deleted == False).all()
        for system in systems_list:
            existing = {
                item.field_id: item
                for item in db.query(SystemFieldValue).filter(SystemFieldValue.system_id == system.id).all()
            }
            changed = False
            for key in legacy_keys:
                field = field_map.get(key)
                if not field:
                    continue
                value = getattr(system, key, None)
                if value is None or str(value).strip() == "":
                    continue
                if field.id in existing:
                    if existing[field.id].value in (None, "", []):
                        existing[field.id].value = value
                        changed = True
                else:
                    db.add(SystemFieldValue(system_id=system.id, field_id=field.id, value=value))
                    changed = True
            if changed:
                db.flush()
        db.commit()
    finally:
        db.close()


def seed_software_field_categories():
    db = SessionLocal()
    try:
        categories = [
            ("软件基本信息", "identity", 1),
            ("授权属性", "license", 2),
            ("合规与时间", "compliance", 3),
            ("财务与采购", "finance", 4),
            ("自定义字段", "custom", 99),
        ]
        category_map = {}
        for name, code, order in categories:
            item = (
                db.query(SoftwareFieldCategory)
                .filter(SoftwareFieldCategory.code == code, SoftwareFieldCategory.is_deleted == False)
                .first()
            )
            if not item:
                item = (
                    db.query(SoftwareFieldCategory)
                    .filter(SoftwareFieldCategory.name == name, SoftwareFieldCategory.is_deleted == False)
                    .first()
                )
            if not item:
                item = SoftwareFieldCategory(name=name, code=code, sort_order=order)
                db.add(item)
                try:
                    db.commit()
                    db.refresh(item)
                except Exception:
                    db.rollback()
                    item = (
                        db.query(SoftwareFieldCategory)
                        .filter(SoftwareFieldCategory.name == name)
                        .first()
                    )
                    if not item:
                        raise
            else:
                if item.code != code:
                    item.code = code
                if item.name != name:
                    item.name = name
                if item.sort_order != order:
                    item.sort_order = order
                db.commit()
            category_map[name] = item.id

        base_fields = [
            ("软件名称", "software_name", "text", "软件基本信息", True, None, 1),
            ("软件版本", "version", "text", "软件基本信息", False, None, 2),
            ("发行商/厂商", "vendor", "text", "软件基本信息", False, None, 3),
            ("软件分类", "category", "single_select", "软件基本信息", False, ["办公软件", "开发工具", "设计工具", "操作系统", "中间件"], 4),
            ("厂商网址", "vendor_url", "text", "软件基本信息", False, None, 5),
            ("授权类型", "license_type", "single_select", "授权属性", False, ["订阅制", "永久授权", "开源"], 1),
            ("计费模式", "billing_mode", "single_select", "授权属性", False, ["按用户", "按设备", "按核心", "站点授权"], 2),
            ("授权密钥", "license_key", "textarea", "授权属性", False, None, 3),
            ("总席位/数量", "total_quantity", "number", "授权属性", False, None, 4),
            ("当前使用数", "used_quantity", "number", "授权属性", False, None, 5),
            ("激活限制", "activation_limit", "text", "授权属性", False, None, 6),
            ("有效期类型", "expiry_type", "single_select", "合规与时间", False, ["固定期限", "永久有效"], 1),
            ("到期日期", "expire_at", "date", "合规与时间", False, None, 2),
            ("续费日期", "renewal_at", "date", "合规与时间", False, None, 3),
            ("合规状态", "compliance_status", "single_select", "合规与时间", False, ["正常", "即将过期", "已过期", "超额使用"], 4),
            ("采购原值", "cost", "number", "财务与采购", False, None, 1),
            ("采购日期", "purchase_date", "date", "财务与采购", False, None, 2),
            ("订单/合同号", "order_no", "text", "财务与采购", False, None, 3),
            ("供应商", "supplier", "text", "财务与采购", False, None, 4),
        ]

        for name, key, ftype, cat_name, required, options, order in base_fields:
            field = (
                db.query(SoftwareField)
                .filter(SoftwareField.field_key == key, SoftwareField.is_deleted == False)
                .first()
            )
            if not field:
                field = SoftwareField(
                    name=name,
                    field_key=key,
                    field_type=ftype,
                    is_required=required,
                    options=options,
                    sort_order=order,
                    category_id=category_map.get(cat_name),
                )
                db.add(field)
            else:
                if field.category_id is None:
                    field.category_id = category_map.get(cat_name)
                if field.options is None and options is not None:
                    field.options = options
            db.commit()

        db.query(SoftwareField).filter(SoftwareField.category_id == None).update(
            {"category_id": category_map.get("自定义字段")}
        )
        db.commit()
    finally:
        db.close()


def seed_office_asset_fields():
    db = SessionLocal()
    try:
        base_fields = [
            ("品牌型号", "brand_model", "text", 1, False, None),
            ("使用人", "user_name", "text", 2, False, None),
            ("所属部门", "dept_name", "text", 3, False, None),
            ("办公地点", "office_location", "text", 4, False, None),
            ("领用日期", "assigned_at", "date", 5, False, None),
            ("供应商", "supplier", "text", 6, False, None),
            ("保修截止", "warranty_due", "date", 7, True, 30),
            ("网络标识", "network_id", "text", 8, False, None),
            ("最近维护日期", "last_maint_at", "date", 9, False, None),
            ("维修记录", "repair_notes", "textarea", 10, False, None),
            ("备注", "remark", "textarea", 11, False, None),
        ]
        categories = (
            db.query(Category)
            .filter(Category.is_deleted == False, Category.usage_scope == "office")
            .all()
        )
        for category in categories:
            for name, key, ftype, order, reminder_enabled, reminder_days in base_fields:
                field = (
                    db.query(CategoryField)
                    .filter(
                        CategoryField.category_id == category.id,
                        CategoryField.field_key == key,
                        CategoryField.is_deleted == False,
                    )
                    .first()
                )
                if not field:
                    field = CategoryField(
                        category_id=category.id,
                        name=name,
                        field_key=key,
                        field_type=ftype,
                        sort_order=order,
                        reminder_enabled=reminder_enabled,
                        reminder_days=reminder_days,
                        usage_scope="office",
                        is_locked=False,
                    )
                    db.add(field)
                else:
                    if field.usage_scope != "office":
                        field.usage_scope = "office"
                    if field.is_locked:
                        field.is_locked = False
                    if reminder_enabled and not field.reminder_enabled:
                        field.reminder_enabled = True
                    if reminder_enabled and field.reminder_days != reminder_days:
                        field.reminder_days = reminder_days
            db.commit()
    finally:
        db.close()


def seed_datacenter_asset_fields():
    db = SessionLocal()
    try:
        base_fields = [
            ("品牌型号", "brand_model", "text", 1, False, None, None),
            ("数据中心/机房", "dc_room", "single_select", 2, False, None, ["机房A", "机房B", "机房C"]),
            ("机柜编号", "cabinet_no", "single_select", 3, False, None, ["柜A", "柜B", "柜C"]),
            ("起始U位", "rack_u_start", "text", 4, False, None, None),
            ("所属项目/业务", "service_name", "text", 5, False, None, None),
            ("保修日期", "warranty_due", "date", 6, True, 30, None),
            ("维保状态", "maintenance_status", "single_select", 7, False, None, ["在保", "过保"]),
            ("维修记录", "repair_notes", "text", 8, False, None, None),
        ]
        categories = (
            db.query(Category)
            .filter(Category.is_deleted == False, Category.usage_scope == "datacenter")
            .all()
        )
        for category in categories:
            for name, key, ftype, order, reminder_enabled, reminder_days, options in base_fields:
                field = (
                    db.query(CategoryField)
                    .filter(
                        CategoryField.category_id == category.id,
                        CategoryField.field_key == key,
                        CategoryField.is_deleted == False,
                    )
                    .first()
                )
                if not field:
                    field = CategoryField(
                        category_id=category.id,
                        name=name,
                        field_key=key,
                        field_type=ftype,
                        sort_order=order,
                        reminder_enabled=reminder_enabled,
                        reminder_days=reminder_days,
                        options=options,
                        usage_scope="datacenter",
                        is_locked=False,
                    )
                    db.add(field)
                else:
                    if field.usage_scope != "datacenter":
                        field.usage_scope = "datacenter"
                    if field.is_locked:
                        field.is_locked = False
                    if options and not field.options:
                        field.options = options
                    if reminder_enabled and not field.reminder_enabled:
                        field.reminder_enabled = True
                    if reminder_enabled and field.reminder_days != reminder_days:
                        field.reminder_days = reminder_days
            db.commit()
    finally:
        db.close()


def seed_dashboard_templates():
    db = SessionLocal()
    try:
        template = (
            db.query(DashboardTemplate)
            .filter(DashboardTemplate.code == "default", DashboardTemplate.is_deleted == False)
            .first()
        )
        if not template:
            template = DashboardTemplate(
                name="默认看板",
                code="default",
                description="系统默认看板模板",
                version=1,
                is_default=True,
                is_published=True,
                is_deleted=False,
            )
            db.add(template)
            db.commit()
            db.refresh(template)

        widget_defs = [
            ("kpi_total_assets", "总资产", "kpi", "kpi_total_assets", 1, 1, 10),
            ("kpi_in_use_rate", "在用率", "kpi", "kpi_in_use_rate", 1, 1, 20),
            ("kpi_repairing", "维修中", "kpi", "kpi_repairing", 1, 1, 30),
            ("kpi_pending_scrap", "待报废", "kpi", "kpi_pending_scrap", 1, 1, 40),
            ("kpi_license_warn", "授权到期预警", "kpi", "kpi_license_warn", 1, 1, 50),
            ("chart_asset_status", "资产状态分布", "chart", "chart_asset_status", 1, 1, 100),
            ("chart_asset_trend", "近12个月新增趋势", "chart", "chart_asset_trend", 1, 1, 110),
            ("chart_license_expiry", "软件授权到期分布", "chart", "chart_license_expiry", 1, 1, 120),
            ("chart_system_dev_lang", "系统开发语言", "chart", "chart_system_dev_lang", 1, 1, 130),
            ("chart_system_status", "系统资产状态", "chart", "chart_system_status", 1, 1, 140),
        ]

        exists = {
            item.widget_key: item
            for item in db.query(DashboardWidget).filter(DashboardWidget.template_id == template.id).all()
        }
        changed = False
        for widget_key, title, widget_type, metric_key, col_span, row_span, sort_order in widget_defs:
            item = exists.get(widget_key)
            if not item:
                db.add(
                    DashboardWidget(
                        template_id=template.id,
                        widget_key=widget_key,
                        title=title,
                        widget_type=widget_type,
                        metric_key=metric_key,
                        col_span=col_span,
                        row_span=row_span,
                        sort_order=sort_order,
                        style_config={"variant": "default", "density": "compact"},
                        data_source_config={},
                        is_active=True,
                    )
                )
                changed = True
            else:
                if item.metric_key != metric_key:
                    item.metric_key = metric_key
                    changed = True
                if item.widget_type != widget_type:
                    item.widget_type = widget_type
                    changed = True
                if item.title != title:
                    item.title = title
                    changed = True
                if item.sort_order != sort_order:
                    item.sort_order = sort_order
                    changed = True
                if item.style_config is None:
                    item.style_config = {"variant": "default", "density": "compact"}
                    changed = True
                if item.data_source_config is None:
                    item.data_source_config = {}
                    changed = True
        if changed:
            db.commit()
    finally:
        db.close()


def seed_dashboard_permissions():
    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.code == "system_admin", Role.is_deleted == False).first()
        if not role:
            return
        for action in ("view", "edit", "publish"):
            exists = (
                db.query(RolePermission)
                .filter(
                    RolePermission.role_id == role.id,
                    RolePermission.resource == "dashboard",
                    RolePermission.action == action,
                )
                .first()
            )
            if not exists:
                db.add(RolePermission(role_id=role.id, resource="dashboard", action=action))
        db.commit()
    finally:
        db.close()


def cleanup_deleted_categories():
    db = SessionLocal()
    try:
        deleted_category_ids = [
            row[0]
            for row in db.query(Category.id).filter(Category.is_deleted == True).all()
        ]
        if deleted_category_ids:
            deleted_field_ids = [
                row[0]
                for row in db.query(CategoryField.id)
                .filter(CategoryField.category_id.in_(deleted_category_ids))
                .all()
            ]
            if deleted_field_ids:
                db.execute(
                    text("DELETE FROM asset_field_values WHERE field_id IN :ids"),
                    {"ids": tuple(deleted_field_ids)},
                )
            db.query(CategoryField).filter(CategoryField.category_id.in_(deleted_category_ids)).delete(
                synchronize_session=False
            )
        db.query(CategoryField).filter(CategoryField.is_deleted == True).delete(synchronize_session=False)
        db.query(Category).filter(Category.is_deleted == True).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def migrate_user_roles():
    db = SessionLocal()
    try:
        roles = {role.code: role for role in db.query(Role).all()}
        needed_roles = [
            ("办公资产管理员", "office_asset_admin"),
            ("数据中心资产管理员", "datacenter_asset_admin"),
        ]
        for name, code in needed_roles:
            if code not in roles:
                role = Role(name=name, code=code)
                db.add(role)
                db.commit()
                db.refresh(role)
                roles[code] = role

        asset_admin = roles.get("asset_admin")
        office_role = roles.get("office_asset_admin")
        datacenter_role = roles.get("datacenter_asset_admin")

        users = db.query(User).filter(User.is_deleted == False).all()
        for user in users:
            if user.role_id:
                db.execute(
                    text(
                        "INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"
                    ),
                    {"uid": user.id, "rid": user.role_id},
                )
            if user.role and user.role.code == "asset_admin":
                target = datacenter_role if user.asset_scope == "datacenter" else office_role
                if target:
                    db.execute(
                        text(
                            "INSERT IGNORE INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"
                        ),
                        {"uid": user.id, "rid": target.id},
                    )
                    user.role_id = target.id

        if asset_admin and not asset_admin.is_deleted:
            asset_admin.is_deleted = True
        if asset_admin:
            db.execute(
                text("DELETE FROM user_roles WHERE role_id = :rid"),
                {"rid": asset_admin.id},
            )

        db.commit()
    finally:
        db.close()
