import motor.motor_asyncio
import os
from loguru import logger
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorDatabase

load_dotenv()

def connectToDatabase() -> AsyncIOMotorDatabase | None:
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL"))
        db = client.VitalGuard
        logger.info("connected to database")
        return db
    except Exception as e:
        logger.error(f"database connection crashed before starting.\n{e}")
        return None