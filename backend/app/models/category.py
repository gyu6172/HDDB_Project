import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key           = Column(String, unique=True, nullable=False)  # "sky" | "land" | "sea"
    label         = Column(String, nullable=False)
    subcategories = relationship("Subcategory", back_populates="category")


class Subcategory(Base):
    __tablename__ = "subcategories"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key         = Column(String, unique=True, nullable=False)
    label       = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    category    = relationship("Category", back_populates="subcategories")
