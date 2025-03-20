# Recipes-LLM

Recipes-LLM let's you create delicious recipes based on user's preferences. Yummy!

## 📌 Overview
The **Recipes-LLM** is a **FastAPI-based backend** that allows users to manage their **ingredient preferences** and generate **personalized recipes**.

### ✨ Features
✅ **Async!**  
✅ **Ingredient Preferences Management** (CRUD operations for user preferences)  
✅ **Automatic Recipes Generation** (Leverages LLMs to generate recipes based on available ingredients and user preferences)  
✅ **Database Cleanup Endpoint** (For testing purposes)  
✅ **FastAPI OpenAPI Docs** for easy API exploration  
✅ **Error Handling & Logging** (Middleware included)  
✅ **CORS Support** for frontend integration  

---

## 🚀 Tech Stack
- **Python 3.12+**  
- **FastAPI** (For API development)  
- **Pydantic v2** (For request/response validation)  
- **SQLAlchemy** (For database interaction)  
- **PostgreSQL** (Database)  
- **Docker** (For containerized database)  
- **Pytest** (For testing)  

---

## 📦 Project Structure

```
recipe
│── app/
│   ├── api/
│   │   ├── endpoints_admin.py                          # Database cleanup endpoint
│   │   ├── endpoints_ingredients.py                    # CRUD operations for ingredient preferences
│   │   ├── endpoints_recipes.py                        # Recipes generation service
│   ├── crud/
│   │   ├── ingredient_preferences_crud.py              # DB operations logic for the ingredient preferences CRUD
│   ├── database/
│   │   ├── database.py                                 # Database session management
│   ├── models/
│   │   ├── models_ingredients.py                       # Database models for the ingredient preferences
│   ├── schemas/
│   │   ├── schema_ingredients.py                       # Pydantic models for the ingredient preferences
│   │   ├── schema_recipes.py                           # Pydantic models for the recipes
│   ├── utils/
│   │   ├── llm_prompts.py                              # LLM prompts for the recipes generation
│   │   ├── llm.py                                      # LLM utility class
│   ├── main.py                                         # FastAPI app entry point
│   ├── tests/
│   │   ├── test_endpoints.py                           # Tests for the fastapi endpoints (ingredient preferences and recipes generation)
│   │   ├── test_recipes.py                             # Tests for the python functions (ingredient preferences and recipes generation)
│── .env                                                # Environment variables (DB config, LLM)
│── docker-compose.yml                                  # Docker config for PostgreSQL
│── requirements.txt                                    # Python dependencies
│── requirements_dev.txt                                # Python dependencies for testing
│── pyproject.toml                                      # Python package metadata
│── README.md                                           # Project documentation
│── LICENSE.md                                          # Project license
```
---

## 🛠️ Setup Instructions  

### 1️ Clone the Repository  
```sh
git clone https://github.com/martimanzano/recipes-llm.git
cd recipe-llm
```

### 2 Set Up a PostgreSQL Database
You can run a local PostgreSQL instance or use Docker:

Using Docker
```sh
docker-compose up -d
```
### 3 Configure Environment Variables
Create a .env file in the root directory:
```code
DATABASE_URL=postgresql://dev-user:password@localhost:5432/recipes_db
CLEAN_DATABASE_PASSWORD=supersecretpassword

LLM_ENDPOINT=https://youropenaicompatiblellmbackend.com/v1beta/openai/
LLM_API_KEY=(your LLM api token)
LLM_MODEL_NAME=(LLM model name). Example: gemini-2.0-flash
```

### 4 Install Dependencies
```sh
pip install -r requirements.txt
```

### 5 Apply Database Migrations
(In this development environment tables in the PostgreSQL will be automatically created when running the service)

### 6 Run the FastAPI Server
```sh
fastapi dev app/main.py 
```

API will be available at: http://127.0.0.1:8000

## 📖 API Documentation
FastAPI automatically generates OpenAPI documentation.

🔗 View API Docs
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc UI: http://127.0.0.1:8000/redoc

## 🧪 Running Tests (and populating the database with some sample data!)
Simply run:
```sh
pyest tests/
```
__IMPORTANT NOTE: IN THIS DEVELOPMENT ENVIRONMENT TESTS WILL USE THE SAME DATABASE_URL CONFIGURED IN THE PROJECT TO EASE TESTING AND DATABASE POPULATING. IN PRODUCTION ENVIRONMENTS A SEPARATE DATABASE SHOULD BE USED.__

---
## Key Design Decisions  

### **Separation of Concerns**
- The project follows a **modular structure** separating database models, business logic, API routes, and schemas.  
- **api/** manages endpoints individually.  
- **crud/** handles database operations separately.  
- **database/** contains database interaction.
- **models/** contains database structures.  
- **schemas** defines data validation using **Pydantic**.  
- **utils/** contains utility classes/variables/functions. For now only for LLM interaction.

### **Ingredient Preferences Model & Validation**  
- Each **ingredient preference** is uniquely identified by `user_id` and `ingredient`.  
- **Constraints prevent contradictions** (e.g., the same ingredient cannot be both "liked" and "disliked").  
- **Enum (`PreferenceEnum`)** ensures only valid preference values are accepted. 
- Prevention of contradictory preferences storing (they need to be setted using the UPDATE method). 

### **Recipes Generation**  
- The recipes generation endpoint takes a list of desired ingredients (enforcing that 3 or more ingredients are passed) and matches each one with the user's preferences. If any of them is disliked, an exception is raised. For the
others, their preference (liked or no preference) is retrieved.
- The preferences-matching is used in a LLM prompt that instructs the model to generate up to 5 recipes taking into account the user's preferences. If no recipes can be generated, the model
is instructed to return an empty list.
- The LLM prompt uses a specific response format define with Pydantic, and the response is also validated before being returned.
- Tested with `Google Gemini 2.0-flash-001`.

### **Admin Cleanup Endpoint**  
- A `/admin/clean-database/` endpoint was added to **reset the database** during testing.  
- Protected by a **secret key** to prevent unauthorized deletions.

### **Others**  
- Logging
- Exception handling
- Function and endpoint testing

Credits
-------
Package structure was created with Cookiecutter and the `audreyr/cookiecutter-pypackage` project template.

- Cookiecutter: https://github.com/audreyr/cookiecutter
- `audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
