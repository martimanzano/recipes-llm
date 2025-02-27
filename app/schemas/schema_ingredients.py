from pydantic import BaseModel, Field
from enum import Enum

class PreferenceEnum(str, Enum):
    liked = "liked"
    disliked = "disliked"

# Base class for common validation
class IngredientPreferenceBase(BaseModel):
    user_id: int = Field(..., ge=0)
    ingredient: str = Field(..., min_length=1)
    preference: PreferenceEnum

# Model for create requests
class IngredientPreferenceCreate(IngredientPreferenceBase):
    pass

# Model for update requests (the ingredient name is in the endpoint itself we don't need it here)
class IngredientPreferenceUpdate(BaseModel):
    preference: PreferenceEnum

# Model for responses
class IngredientPreferenceOut(IngredientPreferenceBase):
    id: int

    model_config = {
        "from_attributes": True,  # for Pydantic v2 compatibility
        # "orm_mode": True
    }