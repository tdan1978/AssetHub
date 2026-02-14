from pydantic import BaseModel

FIELD_TYPES = {
    "text",
    "textarea",
    "number",
    "date",
    "single_select",
    "multi_select",
    "compound",
    "boolean",
}


class SoftwareFieldBase(BaseModel):
    category_id: int | None = None
    name: str
    field_key: str
    field_type: str
    is_required: bool = False
    options: list[str] | list[dict] | None = None
    visibility_rules: list[dict] | None = None
    reminder_enabled: bool = False
    reminder_days: int | None = None
    data_source: str | None = None
    searchable: bool = False
    multi_select_mode: str | None = None
    sort_order: int = 0


class SoftwareFieldCreate(SoftwareFieldBase):
    pass


class SoftwareFieldUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    field_key: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    options: list[str] | list[dict] | None = None
    visibility_rules: list[dict] | None = None
    reminder_enabled: bool | None = None
    reminder_days: int | None = None
    data_source: str | None = None
    searchable: bool | None = None
    multi_select_mode: str | None = None
    sort_order: int | None = None


class SoftwareFieldOut(SoftwareFieldBase):
    id: int
    in_use: bool = False

    class Config:
        from_attributes = True
