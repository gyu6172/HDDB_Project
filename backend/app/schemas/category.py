from pydantic import BaseModel, ConfigDict


class SubcategorySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"key": "shipping", "label": "해운"}},
    )

    key:   str
    label: str


class CategorySchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "key": "sea",
                "label": "바다",
                "subcategories": [
                    {"key": "shipping", "label": "해운"},
                    {"key": "fishery", "label": "수산"},
                ],
            }
        },
    )

    key:           str
    label:         str
    subcategories: list[SubcategorySchema]
