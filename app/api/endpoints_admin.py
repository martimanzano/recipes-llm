import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
from app.database.database import get_db
from app.models.models_ingredients import IngredientPreference

router = APIRouter()
logger = logging.getLogger("admin")

@router.delete("/clean-database", status_code=200)
def clean_database(secret_key: str, db: Session = Depends(get_db)):
    """
    Deletes all data from the database (for testing purposes).
    Requires a secret key for security.
    """
    load_dotenv()    

    if secret_key != os.getenv("CLEAN_DATABASE_PASSWORD"):
        logger.warning(f"{logger.name}: Invalid secret key provided")
        raise HTTPException(status_code=403, detail="Invalid secret key")

    # Delete all records in the table
    ret = db.query(IngredientPreference).delete()
    db.commit()

    message = "Database cleaned successfully. Deleted records: " + str(ret)
    logger.info(message)
    
    return {"message": message}
