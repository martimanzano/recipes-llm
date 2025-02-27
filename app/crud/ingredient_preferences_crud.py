from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.models_ingredients import IngredientPreference
from app.schemas.schema_ingredients import IngredientPreferenceCreate, IngredientPreferenceUpdate

def get_ingredient(db: Session, user_id: int, ingredient_name: str):
    return (
        db.query(IngredientPreference)
        .filter(IngredientPreference.user_id == user_id)
        .filter(IngredientPreference.ingredient == ingredient_name)
        .first()
    )

def create_ingredient(db: Session, igredient_data: IngredientPreferenceCreate):
    existing_preference = get_ingredient(db, igredient_data.user_id, igredient_data.ingredient)
    if existing_preference:
        if existing_preference.preference != igredient_data.preference:
            raise HTTPException(status_code=400, detail="Contradictory preference detected.")
        return existing_preference

    new_preference = IngredientPreference(
        user_id=igredient_data.user_id,
        ingredient=igredient_data.ingredient,
        preference=igredient_data.preference        
    )
    db.add(new_preference)
    db.commit()
    db.refresh(new_preference)

    return new_preference

def update_ingredient(db: Session, user_id: int, igredient_name: str, update_data: IngredientPreferenceUpdate):
    preference = get_ingredient(db, user_id, igredient_name)
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found for the given user."
        )

    preference.preference = update_data.preference
    db.commit()
    db.refresh(preference)

    return preference

def delete_ingredient(db: Session, user_id: int, igredient_name: str):
    preference = get_ingredient(db, user_id, igredient_name)
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found for the given user."
        )

    db.delete(preference)
    db.commit()
    
    return preference

def list_ingredients(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(IngredientPreference).filter(
        IngredientPreference.user_id == user_id
    ).offset(skip).limit(limit).all()