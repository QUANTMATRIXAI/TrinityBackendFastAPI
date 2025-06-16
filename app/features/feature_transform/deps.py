from minio import Minio
import pandas as pd
import io
import os
from io import BytesIO


minio_client = Minio(
    "minioapi.quantmatrixai.com",
    access_key="admin_dev",
    secret_key="pass_dev",
    secure=False
)

def get_minio_df(bucket: str, file_key: str) -> pd.DataFrame:
    response = minio_client.get_object(bucket, file_key)
    content = response.read()
    if file_key.endswith(".csv"):
        df = pd.read_csv(BytesIO(content))
    elif file_key.endswith(".xlsx"):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type")
    return df


from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.config import settings
from fastapi import HTTPException


client = AsyncIOMotorClient(settings.MONGO_URI)


async def get_column_classifications_collection() -> AsyncIOMotorCollection:
    return client["validator_atoms_db"]["column_classifications"]

async def fetch_measures_list(
    validator_atom_id: str,
    file_key: str,
    collection: AsyncIOMotorCollection
) -> list:
    document = await collection.find_one({
        "validator_atom_id": validator_atom_id,
        "file_key": file_key
    })

    if not document or "final_classification" not in document:
        raise HTTPException(status_code=404, detail="Final classification not found in MongoDB")

    measures = document["final_classification"].get("measures", [])

    identifiers = document["final_classification"].get("identifiers", [])
    return identifiers,measures



# In mongodb_saver.py or a shared db file
async def get_transform_settings_collection():
    return client["column_operations_db"]["transform_settings"]