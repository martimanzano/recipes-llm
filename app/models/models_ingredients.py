from sqlalchemy import Column, Integer, String, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class PreferenceEnum(str, enum.Enum):
    liked = "liked"
    disliked = "disliked"

class IngredientPreference(Base):
    __tablename__ = "ingredient_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    ingredient = Column(String, nullable=False)
    preference = Column(Enum(PreferenceEnum), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "ingredient", name="uix_user_ingredient"), # Unique combination of user-ingredient preference constraint
    )