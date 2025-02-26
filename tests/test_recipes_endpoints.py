# tests/test_api.py
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def unique_ingredient(base: str) -> str:
    """Generate a unique ingredient name to avoid collisions between tests."""
    return base#f"{base}-{uuid.uuid4().hex[:6]}"

def test_create_ingredient_preference():
    user_id = 1
    ingredient = unique_ingredient("tomato")
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    response = client.post("/ingredients/", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["ingredient"] == ingredient
    assert data["user_id"] == user_id
    assert data["preference"] == "liked"

def test_create_duplicate_with_same_preference():
    user_id = 2
    ingredient = unique_ingredient("tomato")
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    # First creation should succeed.
    response1 = client.post("/ingredients/", json=payload)
    assert response1.status_code == 201, response1.text
    # Duplicate with same values should return the same record.
    response2 = client.post("/ingredients/", json=payload)
    assert response2.status_code == 201, response2.text
    data = response2.json()
    assert data["ingredient"] == ingredient

def test_create_contradictory_preference():
    user_id = 3
    ingredient = unique_ingredient("lettuce")
    payload1 = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    payload2 = {"user_id": user_id, "ingredient": ingredient, "preference": "disliked"}
    response1 = client.post("/ingredients/", json=payload1)
    assert response1.status_code == 201, response1.text
    response2 = client.post("/ingredients/", json=payload2)
    assert response2.status_code == 400, response2.text
    assert "Contradictory preference" in response2.json()["detail"]

def test_read_ingredient():
    user_id = 4
    ingredient = unique_ingredient("cucumber")
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    client.post("/ingredients/", json=payload)
    response = client.get(f"/ingredients/{ingredient}", params={"user_id": user_id})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ingredient"] == ingredient
    assert data["user_id"] == user_id

def test_update_ingredient():
    user_id = 5
    ingredient = unique_ingredient("onion")
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    client.post("/ingredients/", json=payload)
    update_payload = {"preference": "disliked"}
    response = client.put(f"/ingredients/{ingredient}", params={"user_id": user_id}, json=update_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["preference"] == "disliked"

def test_delete_ingredient():
    user_id = 6
    ingredient = unique_ingredient("garlic")
    payload = {"user_id": user_id, "ingredient": ingredient, "preference": "liked"}
    client.post("/ingredients/", json=payload)
    response = client.delete(f"/ingredients/{ingredient}", params={"user_id": user_id})
    assert response.status_code == 200, response.text
    # Confirm deletion: subsequent read should return a 404.
    response = client.get(f"/ingredients/{ingredient}", params={"user_id": user_id})
    assert response.status_code == 404, response.text

def test_list_ingredients():
    user_id = 7
    # Create several ingredients for the same user.
    ingredients = [
        {"user_id": user_id, "ingredient": unique_ingredient("salt"), "preference": "liked"},
        {"user_id": user_id, "ingredient": unique_ingredient("sugar"), "preference": "disliked"},
        {"user_id": user_id, "ingredient": unique_ingredient("pepper"), "preference": "liked"},
    ]
    for ing in ingredients:
        client.post("/ingredients/", json=ing)
    response = client.get("/ingredients", params={"user_id": user_id})
    assert response.status_code == 200, response.text
    data = response.json()
    # Check that at least the ingredients we just added are present.
    ingredient_names = [item["ingredient"] for item in data]
    for ing in ingredients:
        assert ing["ingredient"] in ingredient_names
