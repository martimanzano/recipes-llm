RECIPES_GENERATION_SYS = "You are a helpful assistant that generates delicious and nutritive recipes from a list of ingredients enclosed in triple quotes."
RECIPES_GENERATION_INST_COMMON = """Generate recipes using the user's preferences enclosed in triple quotes. \
Prioritize the user's liked ingredients over the ones without preferences.

Return an empty list if no recipes can be generated (i.e., insufficient ingredients for being considered complete with culinary sense).

List of ingredients and preferences:
'''{preferences}'''

The number of recipes to generate is up to five, depending on the number of available ingredients. The recipes should be complete and make culinary sense."""

RECIPES_GENERATION_INST = RECIPES_GENERATION_INST_COMMON + """Return your response in a valid JSON document. The JSON object should have the following structure:
[
        {{
            "name": "Recipe title",
            "ingredients_quantitites": [
                {{"ingredient1":"ingredient_name1", "quantity":"quantity of ingredient1"}},
                {{"ingredient2":"ingredient_name2", "quantity":"quantity of ingredient2"}},
                ...],
            "instructions": "Recipe instructions",
            "estimated_cooking_time": "Time in minutes",
            "difficulty_level": "Easy/Medium/Hard",
            "calories": "Calories per serving",
            "servings": "Number of servings"
        }},
        ...
]
"""

RECIPES_GENERATION_INST_STRUCTURED = RECIPES_GENERATION_INST_COMMON