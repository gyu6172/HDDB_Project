from sqlalchemy.orm import Session

from app.core.database import SessionLocal
import app.models.article  # noqa: F401
from app.models.category import Category, Subcategory


SEED_CATEGORIES = [
    {
        "key": "sky",
        "label": "하늘",
        "subcategories": [
            {"key": "bird", "label": "새"},
            {"key": "space", "label": "우주"},
            {"key": "air_pollution", "label": "대기오염"},
            {"key": "weather", "label": "기상"},
        ],
    },
    {
        "key": "land",
        "label": "땅",
        "subcategories": [
            {"key": "disaster", "label": "자연재해"},
            {"key": "animal", "label": "동식물"},
            {"key": "pollution", "label": "환경오염"},
            {"key": "volcano_earthquake", "label": "화산지진"},
        ],
    },
    {
        "key": "sea",
        "label": "바다",
        "subcategories": [
            {"key": "fish", "label": "물고기"},
            {"key": "deep_sea", "label": "심해"},
            {"key": "ocean_pollution", "label": "해양오염"},
            {"key": "marine_life", "label": "해양생물"},
        ],
    },
]


def seed_categories(db: Session) -> None:
    for category_data in SEED_CATEGORIES:
        category = (
            db.query(Category)
            .filter(Category.key == category_data["key"])
            .one_or_none()
        )
        if category is None:
            category = Category(
                key=category_data["key"],
                label=category_data["label"],
            )
            db.add(category)
            db.flush()
        else:
            category.label = category_data["label"]

        for subcategory_data in category_data["subcategories"]:
            subcategory = (
                db.query(Subcategory)
                .filter(
                    Subcategory.category_id == category.id,
                    Subcategory.key == subcategory_data["key"],
                )
                .one_or_none()
            )
            if subcategory is None:
                db.add(
                    Subcategory(
                        key=subcategory_data["key"],
                        label=subcategory_data["label"],
                        category_id=category.id,
                    )
                )
            else:
                subcategory.label = subcategory_data["label"]


def main() -> None:
    db = SessionLocal()
    try:
        seed_categories(db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
