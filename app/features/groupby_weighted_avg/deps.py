import pandas as pd
import io
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from minio import Minio
from fastapi import HTTPException
from .config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)

async def get_validator_atoms_collection() -> AsyncIOMotorCollection:
    return client["validator_atoms_db"]["business_dimensions_with_assignments"]

async def fetch_dimensions_dict(
    validator_atom_id: str,
    file_key: str,
    collection: AsyncIOMotorCollection
) -> dict:
    document = await collection.find_one({
        "validator_atom_id": validator_atom_id,
        "file_key": file_key
    })

    if not document:
        raise HTTPException(status_code=404, detail="Dimension document not found")

    result = {}
    for dim in document.get("dimensions", []):
        dim_id = dim.get("dimension_id")
        result[dim_id] = dim.get("assigned_identifiers", [])
    return result



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
    return measures






import pandas as pd
from minio import Minio
from io import BytesIO
from minio.error import S3Error

minio_client = Minio(
    "minioapi.quantmatrixai.com",
    access_key="admin_dev",
    secret_key="pass_dev",
    secure=False
)

def get_minio_df(bucket_name: str, object_names: str) -> pd.DataFrame:
    response = minio_client.get_object(bucket_name, object_names)
    content = response.read()
    if object_names.endswith(".csv"):
        df = pd.read_csv(BytesIO(content))
    elif object_names.endswith(".xlsx"):
        df = pd.read_excel(BytesIO(content))
    else:
        raise ValueError("Unsupported file type")
    return df


