# app/mongodb_saver.py

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings  # Import the settings object

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
print("Mongo DB in use:", settings.MONGO_DB)


async def save_transform_data(collection_name: str, data: dict):
    await db[collection_name].insert_one(data)


async def save_tansform_data_settings(collection_name: str, data: dict):
    await db[collection_name].insert_one(data) 