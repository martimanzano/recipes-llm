from contextlib import asynccontextmanager
import logging
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.api import endpoints_ingredients, endpoints_recipes, endpoints_admin
from app.database.database import async_engine, Base

# Configure basic logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables if needed
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Close async engine
    await async_engine.dispose()

app = FastAPI(title="Recipe Service", 
              description="A backend service for managing ingredient preferences and creating delicious recipes.",
              version="1.0.0",
              lifespan=lifespan)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as http_exc:
        # Preserve HTTPException responses
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"detail": http_exc.detail},
        )
    except Exception as e:
        # Log and return a generic 500 response for unhandled errors
        logging.error(f"Unhandled error: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error. Please try again later."}
        )
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver", "test"]
)

# Include the routers from the endpoints
app.include_router(endpoints_ingredients.router, prefix="/ingredients")
app.include_router(endpoints_recipes.router, prefix="/recipes")
app.include_router(endpoints_admin.router, prefix="/admin", tags=["Admin"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)