from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models_ingredients import IngredientPreference
from app.schemas.schema_ingredients import IngredientPreferenceCreate, IngredientPreferenceUpdate

async def get_ingredient(db: AsyncSession, user_id: int, ingredient_name: str):
    slct_ret = select(IngredientPreference).filter(
        IngredientPreference.user_id == user_id,
        IngredientPreference.ingredient == ingredient_name
    )
    result = await db.execute(slct_ret)
    preference = result.scalar_one_or_none()
    
    return preference

async def create_ingredient(db: AsyncSession, igredient_data: IngredientPreferenceCreate):
    existing_preference = await get_ingredient(db, igredient_data.user_id, igredient_data.ingredient)
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
    await db.commit()
    await db.refresh(new_preference)

    return new_preference

async def update_ingredient(db: AsyncSession, user_id: int, igredient_name: str, update_data: IngredientPreferenceUpdate):
    preference = await get_ingredient(db, user_id, igredient_name)
    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found for the given user."
        )

    preference.preference = update_data.preference
    await db.commit()
    await db.refresh(preference)

    return preference

async def delete_ingredient(db: AsyncSession, user_id: int, igredient_name: str):
    slct_ret = select(IngredientPreference).filter(
        IngredientPreference.user_id == user_id,
        IngredientPreference.ingredient == igredient_name
    )
    result = await db.execute(slct_ret)
    preference = result.scalar_one_or_none()
    if preference:
        await db.delete(preference)
        await db.commit()
        
        return preference
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found for the given user."
        )

async def list_ingredients(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100):
    slct_ret = select(IngredientPreference).filter(
        IngredientPreference.user_id == user_id
    ).offset(skip).limit(limit)
    result = await db.execute(slct_ret)

    return result.scalars().all()