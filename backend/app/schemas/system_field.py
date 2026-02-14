from pydantic import BaseModel

FIELD_TYPES = {
    "text",
    "textarea",
    "markdown",
    "topology",
    "number",
    "date",
    "single_select",
    "multi_select",
    "compound",
    "boolean",
}


class SystemFieldBase(BaseModel):
    category_id: int | None = None
    name: str
    field_key: str
    field_type: str
    is_required: bool = False
    repeatable: bool = False
    data_source: str | None = None
    searchable: bool = False
    multi_select_mode: str | None = None
    options: list[str] | list[dict] | None = None
    visibility_rules: list[dict] | None = None
    reminder_enabled: bool = False
    reminder_days: int | None = None
    sort_order: int = 0


class SystemFieldCreate(SystemFieldBase):
    pass


class SystemFieldUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = None
    field_key: str | None = None
    field_type: str | None = None
    is_required: bool | None = None
    repeatable: bool | None = None
    data_source: str | None = None
    searchable: bool | None = None
    multi_select_mode: str | None = None
    options: list[str] | list[dict] | None = None
    visibility_rules: list[dict] | None = None
    reminder_enabled: bool | None = None
    reminder_days: int | None = None
    sort_order: int | None = None


class SystemFieldOut(SystemFieldBase):
    id: int
    in_use: bool = False
    is_builtin: bool = False

    class Config:
        from_attributes = True
