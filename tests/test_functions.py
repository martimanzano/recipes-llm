# tests/test_crud.py
import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.endpoints_recipes import create_recipes
from app.database.database import async_engine, async_sessionmaker
from app.crud.ingredient_preferences_crud import (
    create_ingredient,
    get_ingredient,
    update_ingredient,
    delete_ingredient,
    list_ingredients,
)
from app.schemas.schema_ingredients import (
    IngredientPreferenceCreate,
    IngredientPreferenceUpdate,
    PreferenceEnum,
)
from app.schemas.schema_recipes import RecipeList

@pytest_asyncio.fixture(autouse=True, loop_scope="module")
async def db_session():
    """
    Returns a database session using the same production engine.
    In production another database should be used.
    """
    async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest.mark.asyncio(loop_scope="module")
async def test_create_ingredient_preference(db_session: AsyncSession):
    print("test_create_ingredient_preference")
    user_id = 1
    ingredient = "tomato"
    create_payload = IngredientPreferenceCreate(
        user_id=user_id,
        ingredient=ingredient,
        preference=PreferenceEnum.liked
    )
    record = await create_ingredient(db_session, create_payload)
    assert record.ingredient == ingredient
    assert record.user_id == user_id
    assert record.preference.value == PreferenceEnum.liked

@pytest.mark.asyncio(loop_scope="module")
async def test_create_duplicate_with_same_preference(db_session: AsyncSession):
    user_id = 2
    ingredient = "tomato"
    payload = IngredientPreferenceCreate(
        user_id=user_id,
        ingredient=ingredient,
        preference=PreferenceEnum.liked
    )
    record1 = await create_ingredient(db_session, payload)
    record2 = await create_ingredient(db_session, payload)
    # The duplicate creation should return the existing record.
    assert record1.id == record2.id
    assert record1.ingredient == record2.ingredient


@pytest.mark.asyncio(loop_scope="module")
async def test_create_contradictory_preference(db_session: AsyncSession):
    user_id = 3
    ingredient = "lettuce"
    payload1 = IngredientPreferenceCreate(
        user_id=user_id,
        ingredient=ingredient,
        preference=PreferenceEnum.liked
    )
    payload2 = IngredientPreferenceCreate(
        user_id=user_id,
        ingredient=ingredient,
        preference=PreferenceEnum.disliked
    )
    # Create the initial record.
    record1 = await create_ingredient(db_session, payload1)
    with pytest.raises(HTTPException) as exc_info:
        await create_ingredient(db_session, payload2)
    # Verify that the error message indicates a contradictory preference.
    assert "Contradictory preference" in str(exc_info.value)

@pytest.mark.asyncio(loop_scope="module")
async def test_get_update_delete_ingredient(db_session: AsyncSession):
    user_id = 4
    ingredient = "cucumber"
    # Create record.
    create_payload = IngredientPreferenceCreate(
        user_id=user_id,
        ingredient=ingredient,
        preference=PreferenceEnum.liked
    )
    record = await create_ingredient(db_session, create_payload)
    # Retrieve record.
    record_get = await get_ingredient(db_session, user_id, ingredient)
    assert record_get is not None
    assert record_get.id == record.id

    # Update record.
    update_payload = IngredientPreferenceUpdate(preference=PreferenceEnum.disliked)
    updated_record = await update_ingredient(db_session, user_id, ingredient, update_payload)
    assert updated_record.preference.value == PreferenceEnum.disliked

    # Delete record.
    deleted_record = await delete_ingredient(db_session, user_id, ingredient)
    # Ensure the record is removed.
    record_after_delete = await get_ingredient(db_session, user_id, ingredient)
    assert record_after_delete is None

@pytest.mark.asyncio(loop_scope="module")
async def test_list_ingredients(db_session: AsyncSession):
    user_id = 5
    ingredients_data = [
        {"ingredient": "salt", "preference": PreferenceEnum.liked},
        {"ingredient": "sugar", "preference": PreferenceEnum.disliked},
        {"ingredient": "pepper", "preference": PreferenceEnum.liked},
    ]
    # Create several ingredient preference records.
    for data in ingredients_data:
        payload = IngredientPreferenceCreate(
            user_id=user_id,
            ingredient=data["ingredient"],
            preference=data["preference"]
        )
        await create_ingredient(db_session, payload)
    records = await list_ingredients(db_session, user_id, skip=0, limit=100)
    returned_ingredients = {record.ingredient for record in records}
    for data in ingredients_data:
        assert data["ingredient"] in returned_ingredients

@pytest.mark.asyncio(loop_scope="module")
async def test_create_recipes_with_disliked_ingredients(db_session: AsyncSession):
    user_id = 1
    ingredients = ["tomato", "cheese", "onion"]

    # Create some preferences in the DB
    await create_ingredient(db_session, IngredientPreferenceCreate(user_id=user_id, ingredient="tomato", preference="liked"))
    await create_ingredient(db_session, IngredientPreferenceCreate(user_id=user_id, ingredient="onion", preference="disliked"))

    with pytest.raises(HTTPException) as exc_info:
        result = await create_recipes(user_id, ingredients, db_session)
    # Verify that the error message indicates a contradictory preference.
    assert "disliked ingredients" in str(exc_info.value).lower()

@pytest.mark.asyncio(loop_scope="module")
async def test_create_recipes_with_insufficient_ingredients(db_session: AsyncSession):
    user_id = 1
    ingredients = ["salt", "oil", "sugar"]
  
    with pytest.raises(HTTPException) as exc_info:
        result = await create_recipes(user_id, ingredients, db_session)
    # Verify that the error message indicates a contradictory preference.
    assert "no recipes found" in str(exc_info.value).lower()

@pytest.mark.asyncio(loop_scope="module")
async def test_create_recipes(db_session: AsyncSession):
    user_id = 13
    ingredients = ["tomato", "cheese", "onion", "salt", "pepper", "chicken", "garlic", "oil", "rice", "paprika", "curry"]
    
    result = await create_recipes(user_id, ingredients, db_session)
        
    assert result is not None
    assert isinstance(result, RecipeList)
    assert len(result.root) > 0