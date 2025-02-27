import logging
from fastapi import FastAPI
import uvicorn
from app.api import endpoints_ingredients, endpoints_recipes, endpoints_admin
from app.database.database import engine
from app.models.models_ingredients import Base

# Configure logging (you could also configure a more advanced logging framework)
logging.basicConfig(level=logging.INFO)

# Create database tables if needed
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Recipe Service", 
              version="1.0.0", 
              description="A backend service for managing ingredient preferences and creating delicious recipes.")

# Include the ingredient preferences router under a common prefix
app.include_router(endpoints_ingredients.router, prefix="/ingredients")
app.include_router(endpoints_recipes.router, prefix="/recipes")
app.include_router(endpoints_admin.router, prefix="/admin", tags=["Admin"])

# Optionally add middleware for error handling, CORS, etc.

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)