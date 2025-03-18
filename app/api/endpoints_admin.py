import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from dotenv import load_dotenv
import os
from app.database.database import get_db
from app.models.models_ingredients import IngredientPreference

router = APIRouter()
logger = logging.getLogger("admin")

@router.delete("/clean-database", status_code=200)
async def clean_database(secret_key: str, db: AsyncSession = Depends(get_db)):
    """
    Deletes all data from the database (for testing purposes).
    Requires a secret key for security.
    """
    load_dotenv()    

    if secret_key != os.getenv("CLEAN_DATABASE_PASSWORD"):
        logger.warning(f"{logger.name}: Invalid secret key provided")
        raise HTTPException(status_code=403, detail="Invalid secret key")

    # Delete all records in the table
    slct_ret = select(IngredientPreference)
    ret = await db.execute(slct_ret)
    for record in ret.scalars():
        db.delete(record)
    await db.commit()

    message = "Database cleaned successfully. Deleted records: " + str(ret)
    logger.info(message)
    
    return {"message": message}
