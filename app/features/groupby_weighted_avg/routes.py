from fastapi import APIRouter, Form,HTTPException
from typing import Dict
# from .minio_utils import get_minio_df
from .deps import get_minio_df,get_validator_atoms_collection, fetch_dimensions_dict, get_column_classifications_collection,fetch_measures_list,minio_client
from .mongodb_saver import save_groupby_result
from typing import List,Optional
import io
import json
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from groupby.base import perform_groupby as groupby_base_func,get_resample_options  # or your correct import path

from io import BytesIO
import datetime

# app/core/store.py or at the top of app/routes.py
groupby_store = {}

router = APIRouter()

@router.post("/init")
async def get_dimensions_and_measures(
    bucket_name: str = Form(...),
    object_names: str = Form(...),
    validator_atom_id: str = Form(...),
    file_key: str = Form(...)
) -> Dict:
    # Step 1: Read file from MinIO
    df = get_minio_df(bucket_name, object_names)

    df.columns = [col.strip().lower() for col in df.columns]

    # Step 2: Get assigned dimensions
    dimensions_collection = await get_validator_atoms_collection()
    dimensions = await fetch_dimensions_dict(validator_atom_id, file_key, dimensions_collection)

    # Step 3: Get final measures from column_classifications
    measures_collection = await get_column_classifications_collection()
    final_measures = await fetch_measures_list(validator_atom_id, file_key, measures_collection)

    # Step 4: Auto-detect numeric columns as fallback/reference
    numeric_measures = df.select_dtypes(include='number').columns.tolist()

    if 'date' in df.columns:
        df = df.sort_values(by='date')

    # Step 5: Detect time frequency if time-related column exists
    frequency = None
    time_col_found = None
    time_cols = ['date']

    return {
        "dimensions_from_db": dimensions,
        "measures_from_db": final_measures,
        "time_column_used": time_col_found,
    }


@router.post("/run")
async def perform_groupby_route(
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    bucket_name: str = Form(...),
    object_names: str = Form(...),
    identifiers: List[str] = Form(...),
    aggregations: str = Form(...),
   
):
    try:
        aggregations = json.loads(aggregations)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in aggregations")

    df = get_minio_df(bucket_name=bucket_name, object_names=object_names)
    df.columns = [col.strip().lower() for col in df.columns]

    time_col = "date" if "date" in df.columns else None

    grouped = groupby_base_func(df, identifiers, aggregations)

    groupby_store["grouped_result"] = grouped
    # await save_groupby_result(validator_atom_id, file_key, grouped)


    # Save to MinIO with new filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{validator_atom_id}_{file_key}_grouped.csv"    

    csv_bytes  = grouped.to_csv(index=False).encode("utf-8")

    # assuming you already have a MinIO client called `minio_client`
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=new_filename,
        data=io.BytesIO(csv_bytes),
        length=len(csv_bytes),
        content_type="text/csv"
    )

    return {
        "message": "GroupBy complete",
        # "preview": grouped.head(5).to_dict(orient="records")
    }

@router.get("/results")
async def get_latest_groupby_result_from_minio(
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    bucket_name: str = Form(...),
):
    try:
        key = f"{validator_atom_id}_{file_key}_grouped.csv"

        # Read the merged file back from MinIO
        group_obj = minio_client.get_object(bucket_name, key)
        grouped_df = pd.read_csv(io.BytesIO(group_obj.read()))

        return {
            "row_count": len(grouped_df),
            "merged_data": grouped_df.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Unable to fetch merged data: {str(e)}")

