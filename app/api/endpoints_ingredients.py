import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.schemas import schema_ingredients as schemas
from app.crud import ingredient_preferences_crud as crud
from app.database.database import get_db

router = APIRouter()
logger = logging.getLogger("ingredient_preference")
logger.setLevel(logging.INFO)

@router.post("/", response_model=schemas.IngredientPreferenceOut, status_code=status.HTTP_201_CREATED)
def create_ingredient_preference(
    preference: schemas.IngredientPreferenceCreate, 
    db: Session = Depends(get_db)
):
    logger.info("Creating ingredient preference for user %s and ingredient '%s'", preference.user_id, preference.ingredient)
    return crud.create_ingredient(db, preference)

@router.get("/", response_model=list[schemas.IngredientPreferenceOut])
def read_ingredients(
    user_id: int = Query(..., gt=0), 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return crud.list_ingredients(db, user_id, skip, limit)

@router.get("/{ingredient}", response_model=schemas.IngredientPreferenceOut)
def read_ingredient(
    ingredient: str, 
    user_id: int = Query(..., gt=0), 
    db: Session = Depends(get_db)
):
    record = crud.get_ingredient(db, user_id, ingredient)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found for the given user."
        )
    return record

@router.put("/{ingredient}", response_model=schemas.IngredientPreferenceOut)
def update_ingredient_preference(
    ingredient: str, 
    update: schemas.IngredientPreferenceUpdate,
    user_id: int = Query(..., gt=0), 
    db: Session = Depends(get_db)
):
    logger.info("Updating ingredient '%s' for user %s", ingredient, user_id)
    return crud.update_ingredient(db, user_id, ingredient, update)

@router.delete("/{ingredient}", response_model=schemas.IngredientPreferenceOut)
def delete_ingredient_preference(
    ingredient: str, 
    user_id: int = Query(..., gt=0), 
    db: Session = Depends(get_db)
):
    logger.info("Deleting ingredient '%s' for user %s", ingredient, user_id)
    return crud.delete_ingredient(db, user_id, ingredient)