# tests/test_api.py
import pytest
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
from app.main import app
from app.schemas.schema_recipes import RecipeList
from app.database.database import async_engine


@pytest_asyncio.fixture(scope="module", loop_scope="module", autouse=True)
async def test_life_cycle():
    yield
    await async_engine.dispose()

@pytest.mark.asyncio(loop_scope="module")
async def test_create_ingredient_preference():
    print("test_create_ingredient_preference")
    user_id = 1
    ingredient = "tomato"
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/ingredients/", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["ingredient"] == ingredient
    assert data["user_id"] == user_id
    assert data["preference"] == "liked"

@pytest.mark.asyncio(loop_scope="module")
async def test_create_duplicate_with_same_preference():
    user_id = 2
    ingredient = "tomato"
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    # First creation should succeed.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response1 = await client.post("/ingredients/", json=payload)
        assert response1.status_code == 201, response1.text
        # Duplicate with same values should return the same record.
        response2 = await client.post("/ingredients/", json=payload)
        assert response2.status_code == 201, response2.text
        data = response2.json()
    assert data["ingredient"] == ingredient

@pytest.mark.asyncio(loop_scope="module")
async def test_create_contradictory_preference():
    user_id = 3
    ingredient = "lettuce"
    payload1 = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    payload2 = {"user_id": user_id, "ingredient": ingredient, "preference": "disliked"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response1 = await client.post("/ingredients/", json=payload1)
        assert response1.status_code == 201, response1.text
        response2 = await client.post("/ingredients/", json=payload2)
        assert response2.status_code == 400, response2.text
        assert "Contradictory preference" in response2.json()["detail"]

@pytest.mark.asyncio(loop_scope="module")
async def test_read_ingredient():
    user_id = 4
    ingredient = "cucumber"
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/ingredients/", json=payload)
        response = await client.get(f"/ingredients/{ingredient}", params={"user_id": user_id})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["ingredient"] == ingredient
        assert data["user_id"] == user_id

@pytest.mark.asyncio(loop_scope="module")
async def test_update_ingredient():
    user_id = 5
    ingredient = "onion"
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/ingredients/", json=payload)
        update_payload = {"preference": "disliked"}
        response = await client.put(f"/ingredients/{ingredient}", params={"user_id": user_id}, json=update_payload)
        assert response.status_code == 200, response.text
        data = response.json()
    assert data["preference"] == "disliked"

@pytest.mark.asyncio(loop_scope="module")
async def test_delete_ingredient():
    user_id = 6
    ingredient = "garlic"
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/ingredients/", json=payload)
        response = await client.delete(f"/ingredients/{ingredient}", params={"user_id": user_id})
        assert response.status_code == 200, response.text
        # Confirm deletion: subsequent read should return a 404.
        response = await client.get(f"/ingredients/{ingredient}", params={"user_id": user_id})
    assert response.status_code == 404, response.text

@pytest.mark.asyncio(loop_scope="module")
async def test_list_ingredients():
    user_id = 7
    # Create several ingredients for the same user.
    ingredients = [
        {"user_id": user_id, "ingredient": "salt", "preference": "liked"},
        {"user_id": user_id, "ingredient": "sugar", "preference": "disliked"},
        {"user_id": user_id, "ingredient": "pepper", "preference": "liked"},
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for ing in ingredients:
            await client.post("/ingredients/", json=ing)
        response = await client.get("/ingredients/", params={"user_id": user_id})
        assert response.status_code == 200, response.text
        data = response.json()
        # Check that at least the ingredients we just added are present.
        ingredient_names = [item["ingredient"] for item in data]
    for ing in ingredients:
        assert ing["ingredient"] in ingredient_names

@pytest.mark.asyncio(loop_scope="module")
async def test_create_recipes_with_disliked_ingredients():
    user_id = 11
    # Create several ingredients for the same user.
    ingredients = ["tomato", "cheese", "onion"]
    
    ingredients_preferences = [
        {"user_id": user_id, "ingredient": ingredients[0], "preference": "liked"},
        {"user_id": user_id, "ingredient": ingredients[1], "preference": "liked"},
        {"user_id": user_id, "ingredient": ingredients[2], "preference": "disliked"}
    ]

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/ingredients/", json=ingredients_preferences[0])
        await client.post("/ingredients/", json=ingredients_preferences[1])
        await client.post("/ingredients/", json=ingredients_preferences[2])
    
        response = await client.get("/recipes/", params={"user_id": user_id, "ingredients": ingredients})
        assert response.status_code == 400, response.json()
        assert "disliked ingredients" in str(response.json()["detail"]).lower()

@pytest.mark.asyncio(loop_scope="module")
async def test_create_recipes_with_insufficient_ingredients():
    user_id = 11
    ingredients = ["salt", "oil", "sugar"]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/recipes/", params={"user_id": user_id, "ingredients": ingredients})
        assert response.status_code == 400, response.json()
        assert "no recipes found" in str(response.json()["detail"]).lower()
  
@pytest.mark.asyncio(loop_scope="module")
async def test_create_recipes():
    user_id = 13
    ingredients = ["tomato", "cheese", "onion", "salt", "pepper", "chicken", "garlic", "oil", "rice", "paprika", "curry"]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/recipes/", params={"user_id": user_id, "ingredients": ingredients})
        
        assert response is not None
        recipe_list_obj = RecipeList.model_validate(response.json())
        assert recipe_list_obj
        assert len(recipe_list_obj.root) > 0