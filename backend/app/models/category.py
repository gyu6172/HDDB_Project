import uuid
from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key           = Column(String, unique=True, nullable=False)  # "sky" | "land" | "sea"
    label         = Column(String, nullable=False)
    subcategories = relationship("Subcategory", back_populates="category")
    articles      = relationship("Article", back_populates="category_rel")


class Subcategory(Base):
    __tablename__ = "subcategories"
    __table_args__ = (
        UniqueConstraint("category_id", "key", name="uq_subcategories_category_id_key"),
    )

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key         = Column(String, nullable=False)
    label       = Column(String, nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    category    = relationship("Category", back_populates="subcategories")
    articles    = relationship("Article", back_populates="subcategory_rel")
