from pydantic import BaseModel


class SubcategorySchema(BaseModel):
    key:   str
    label: str

    class Config:
        from_attributes = True


class CategorySchema(BaseModel):
    key:           str
    label:         str
    subcategories: list[SubcategorySchema]

    class Config:
        from_attributes = True
