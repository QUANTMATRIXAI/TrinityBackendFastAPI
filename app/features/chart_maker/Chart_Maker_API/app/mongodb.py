from motor.motor_asyncio import AsyncIOMotorClient
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


MONGO_URI = "mongodb://admin_dev:pass_dev@10.2.1.65:9005/?authSource=admin"
client = AsyncIOMotorClient("mongodb://admin_dev:pass_dev@10.2.1.65:9005/?authSource=admin")
db = client["Filter_data"]
collection_filter = db["filters"]


async def check_mongodb_connection():
    client = AsyncIOMotorClient(MONGO_URI)
    try:
        await client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return {"status": "MongoDB connection successful"}
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}", exc_info=True)
        raise
    finally:
        client.close()

async def save_filters(metadata: dict) -> dict:
    try:
        await collection_filter.insert_one(metadata)
    except Exception as e:
        logger.error(f"MongoDB error: {e}", exc_info=True)
        raise

async def get_filter(filter_id: str):
    doc = await collection_filter.find_one({"filter_id": filter_id})
    if not doc:
        raise ValueError("Document not found")
    return doc["filters_applied"]
    