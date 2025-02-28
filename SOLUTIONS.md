# Solution Approach

## Overview  
The **Recipes-llm API** has been implemented trying to take into account all the specified requirements, i.e., Python 3.12, FastAPI, Pydantic v2, Database persistance and OpenAI compatible-LLM.  

---

## Design Approach  

### **Separation of Concerns**
- The project follows a **modular structure** separating database models, business logic, API routes, and schemas.  
- **api/** manages endpoints individually.  
- **crud/** handles database operations separately.  
- **database/** contains database interaction.
- **models/** contains database structures.  
- **schemas** defines data validation using **Pydantic**.  
- **utils/** contains utility classes/variables/functions. For now only for LLM interaction.

### **Database and ORM**  
- **PostgreSQL** as database.  
- **SQLAlchemy** as the ORM.  

---

## Key Design Decisions  

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
- The LLM used was `Google Gemini 2.0-flash-001`.

### **Admin Cleanup Endpoint**  
- A `/admin/clean-database/` endpoint was added to **reset the database** during testing.  
- Protected by a **secret key** to prevent unauthorized deletions.

### **Others**  
- Logging
- Exception handling
- Function and endpoint testing

---

## Challenges

- Some errors were returning 500 Internal Server Error instead of custom responses. Solution: Middleware was added to preserve FastAPI's HTTPExceptions while catching the others.
- Fastapi was rejecting pytest calls in test_endpoints.py (`Invalid host header`). Solution: Add `testserver` to the trusted hosts in the middleware.
- Some prompt engineering was needed to get good results. Using a more powerful LLM would probably yield better results.

---

## Areas for Future Improvements  
- In-context learning to improve the recipes generation.
- Validation of the generated recipes using another LLM.
- Recipes feedback
...
  
---
