from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.database import Base, engine, SessionLocal
from app.models.system_field_category import SystemFieldCategory
from app.models.system_field import SystemField
from app.models.software_field_category import SoftwareFieldCategory
from app.models.software_field import SoftwareField
from app.routers import auth, assets, asset_fields, licenses, users, roles, stocktakes, dashboard, categories, maintenance, systems, system_fields, system_field_categories, software_field_categories, license_fields, notifications

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


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
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
    seed_software_field_categories()


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
                .filter(SystemFieldCategory.code == code, SystemFieldCategory.is_deleted == False)
                .first()
            )
            if not item:
                item = (
                    db.query(SystemFieldCategory)
                    .filter(SystemFieldCategory.name == name, SystemFieldCategory.is_deleted == False)
                    .first()
                )
            if not item:
                item = SystemFieldCategory(name=name, code=code, sort_order=order)
                db.add(item)
                db.commit()
                db.refresh(item)
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
            ("系统名称", "app_name", "text", "基础字段", True, None, 1),
            ("系统编码", "app_code", "text", "基础字段", True, None, 2),
            ("系统状态", "app_status", "single_select", "基础字段", False, ["开发中", "测试中", "运行中", "维护中", "已下线"], 3),
            ("访问地址 (URL)", "access_url", "text", "基础字段", False, None, 4),
            ("系统分类", "app_category", "single_select", "基础字段", False, ["业务系统", "工具系统", "中间件", "内部平台"], 5),
            ("架构类型", "arch_type", "single_select", "技术栈与环境", False, ["B/S", "C/S", "微服务", "单体架构"], 1),
            ("开发语言", "dev_lang", "single_select", "技术栈与环境", False, ["Python", "Java", "Go", "PHP"], 2),
            ("数据库", "db_type", "single_select", "技术栈与环境", False, ["MySQL", "PostgreSQL", "Oracle", "Redis"], 3),
            ("部署方式", "deploy_type", "single_select", "技术栈与环境", False, ["物理机部署", "虚拟机部署", "容器化 (K8s)"], 4),
            ("源代码地址", "repo_url", "text", "技术栈与环境", False, None, 5),
            ("业务负责人", "biz_owner", "text", "管理与运维", False, None, 1),
            ("技术负责人", "tech_owner", "text", "管理与运维", False, None, 2),
            ("运维负责人", "ops_owner", "text", "管理与运维", False, None, 3),
            ("等级保护级别", "sec_level", "single_select", "管理与运维", False, ["等保一级", "等保二级", "等保三级"], 4),
        ]

        for name, key, ftype, cat_name, required, options, order in base_fields:
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
                )
                db.add(field)
            else:
                if field.category_id is None:
                    field.category_id = category_map.get(cat_name)
                if field.options is None and options is not None:
                    field.options = options
            db.commit()

        db.query(SystemField).filter(SystemField.category_id == None).update(
            {"category_id": category_map.get("自定义字段")}
        )
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
                db.commit()
                db.refresh(item)
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
