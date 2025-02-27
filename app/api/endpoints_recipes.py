import logging
from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.database import get_db
from pydantic import BaseModel
from app.utils.llm import GenericLLM
import app.utils.llm_prompts as llm_prompts
import app.schemas.schema_recipes as schemas_recipes

from app.models.models_ingredients import IngredientPreference, PreferenceEnum

router = APIRouter()
logger = logging.getLogger("recipes")
logger.setLevel(logging.INFO)

class IngredientList(BaseModel):
    names: list = []

@router.get("/", response_model=schemas_recipes.RecipeList)
def create_recipes(
    user_id: int = Query(..., gt=0), 
    ingredients: List[str] = Query(..., min_length=3), 
    db: Session = Depends(get_db)
):
    preferences = (
        db.query(IngredientPreference)
        .filter(IngredientPreference.user_id == user_id, IngredientPreference.ingredient.in_(ingredients))
        .all()
    )
    # Create a mapping of ingredient -> preference
    preference_map = {p.ingredient: p.preference.value for p in preferences}
    if PreferenceEnum.disliked in preference_map.values():
        raise HTTPException(status_code=400, detail="Cannot generate recipes with disliked ingredients")
    # Add "no preference" for ingredients that were not found
    result = {ingredient: preference_map.get(ingredient, "no preference") for ingredient in ingredients}
  
    llm = GenericLLM()
    formatted_prompt = llm.build_prompt(llm_prompts.RECIPES_GENERATION_SYS, None, llm_prompts.RECIPES_GENERATION_INST_STRUCTURED.format(preferences=result))
    structured_llm_response = llm.generate_structured_response(formatted_prompt, schemas_recipes.RecipeList, 0.6, 4096)
    recipe_list_obj = schemas_recipes.RecipeList.model_validate(structured_llm_response)
    
    return recipe_list_obj