from pydantic import BaseModel, Field, RootModel
from typing import List

class Ingredient(BaseModel):
    ingredient: str = Field(..., description="The name of the ingredient.")
    quantity: str = Field(..., description="The quantity of the ingredient.")

class Recipe(BaseModel):
    name: str = Field(..., description="The title of the recipe.")
    ingredients_quantities: List[Ingredient] = Field(
        ..., description="List of ingredients with their quantities."
    )
    instructions: str = Field(..., description="Detailed recipe instructions.")
    estimated_cooking_time: str = Field(
        ..., description="Estimated cooking time in minutes."
    )
    difficulty_level: str = Field(
        ..., description="Difficulty level of the recipe (Easy/Medium/Hard)."
    )
    calories: str = Field(..., description="Calories per serving.")
    servings: int = Field(..., description="Number of servings.")

class RecipeList(RootModel[List[Recipe]]):
    pass