import logging
from fastapi import FastAPI
from sqlalchemy import text
from app.api import endpoints
from app.database import engine, SessionLocal
from app.ingredient_preferences_crud import create_ingredient
from app.models import Base
from app.pydantic_schema import IngredientPreferenceCreate

# Configure logging (you could also configure a more advanced logging framework)
logging.basicConfig(level=logging.INFO)

# Create database tables if needed (in production consider using migrations like Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Service", 
              version="1.0.0", 
              description="A backend service for managing ingredient preferences.")

# Include the ingredient preferences router under a common prefix
app.include_router(endpoints.router, prefix="/ingredients")

# Optionally add middleware for error handling, CORS, etc.

# user_id = 1
# ingredient = "tomato"
# create_payload = IngredientPreferenceCreate(
#     user_id=user_id,
#     ingredient=ingredient,
#     preference="liked"
# )
# record = create_ingredient(SessionLocal(), create_payload)
