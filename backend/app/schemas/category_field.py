from pydantic import BaseModel

FIELD_TYPES = {
    "text",
    "textarea",
    "number",
    "date",
    "single_select",
    "multi_select",
    "boolean",
}


class CategoryFieldBase(BaseModel):
    name: str
    field_key: str
    field_type: str
    is_required: bool = False
    options: list[str] | None = None
    visibility_rules: list[dict] | None = None
    reminder_enabled: bool = False
    reminder_days: int | None = None
    sort_order: int = 0


class CategoryFieldCreate(CategoryFieldBase):
    pass


class CategoryFieldUpdate(BaseModel):
    name: str | None = None
    field_key: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    options: list[str] | None = None
    visibility_rules: list[dict] | None = None
    reminder_enabled: bool | None = None
    reminder_days: int | None = None
    sort_order: int | None = None


class CategoryFieldOut(CategoryFieldBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True
