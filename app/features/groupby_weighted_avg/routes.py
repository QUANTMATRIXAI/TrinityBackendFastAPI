from fastapi import APIRouter, Form,HTTPException
from typing import Dict
# from .minio_utils import get_minio_df
from .deps import get_minio_df,get_validator_atoms_collection, fetch_dimensions_dict, get_column_classifications_collection,fetch_measures_list,upload_fileobj_to_minio
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

    # for col in df.columns:
    #     if col.lower() in time_cols:
    #         try:
    #             parsed = pd.to_datetime(df[col], errors='coerce').dropna().drop_duplicates()
    #             parsed = parsed.sort_values()

    #             if len(parsed) >= 3:
    #                 inferred = pd.infer_freq(parsed)
    #                 if inferred:
    #                     frequency = inferred
    #                     time_col_found = col
    #                     break
    #         except Exception:
    #             continue

    # resample_suggestions = get_resample_options(frequency) if frequency else []


    return {
        "dimensions_from_db": dimensions,
        "measures_from_db": final_measures,
        "time_column_used": time_col_found,
        # "inferred_frequency": frequency,
        # # "detected_measures": numeric_measures,
        # # "columns_in_file": df.columns.tolist()
        # "resample_suggestions": resample_suggestions
    }


@router.post("/run")
async def perform_groupby_route(
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    bucket_name: str = Form(...),
    object_names: str = Form(...),
    identifiers: List[str] = Form(...),
    aggregations: str = Form(...),
    resample_to: Optional[str] = Form(None)  # e.g., "M", "W", "Q"
):
    try:
        aggregations = json.loads(aggregations)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in aggregations")

    df = get_minio_df(bucket_name=bucket_name, object_names=object_names)
    df.columns = [col.strip().lower() for col in df.columns]

    time_col = "date" if "date" in df.columns else None

    # if resample_to:
    #     # RESAMPLE LOGIC
    #     resample_to = resample_to.strip().strip('"').strip("'")
    #     if not time_col:
    #         raise HTTPException(status_code=400, detail="Cannot resample: no 'date' column found.")
        
    #     # Convert to datetime and clean
    #     df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    #     df = df.dropna(subset=[time_col])
    #     df = df.sort_values(by=time_col)
        
    #     # Create resampled period column
    #     resample_col = 'resampled_period'
    #     df[resample_col] = df[time_col].dt.to_period(resample_to).dt.to_timestamp()

    #     df.drop(columns=[time_col], inplace=True)

    #     # Remove time_col if it exists in identifiers
    #     if time_col in identifiers:
    #         identifiers.remove(time_col)

    #     # Use your custom groupby function with the resampled period
    #     grouped = groupby_base_func(df, identifiers + [resample_col], aggregations)
        
    #     # Rename the resampled column back to original name
    #     grouped = grouped.rename(columns={resample_col: time_col})
        
    #     # Sort by date if present
    #     if time_col in grouped.columns:
    #         grouped = grouped.sort_values(by=time_col)
    # else:
    #     # REGULAR GROUPBY LOGIC
    grouped = groupby_base_func(df, identifiers, aggregations)

    groupby_store["grouped_result"] = grouped
    # await save_groupby_result(validator_atom_id, file_key, grouped)


    # Save to MinIO with new filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"{file_key}_grouped_{timestamp}.parquet"

    buffer = BytesIO()
    grouped.to_parquet(buffer, index=False)
    buffer.seek(0)

    await upload_fileobj_to_minio(
        bucket_name=bucket_name,
        object_name=new_filename,
        file_obj=buffer,
        content_type="application/octet-stream"
    )


    return {
        "message": "GroupBy complete",
        # "preview": grouped.head(5).to_dict(orient="records")
    }

@router.get("/results")
async def get_latest_groupby_result_from_minio(
    bucket_name: str,
    file_key: str
):
    from .deps import minio_client
    import pandas as pd

    try:
        # Step 1: List all objects in the bucket
        objects = minio_client.list_objects(bucket_name, recursive=True)
        matching_files = []

        for obj in objects:
            if obj.object_name.startswith(f"{file_key}_grouped_") and obj.object_name.endswith(".parquet"):
                matching_files.append(obj)

        if not matching_files:
            raise HTTPException(status_code=404, detail="No grouped files found in MinIO.")

        # Step 2: Sort by last modified to get latest
        latest_file = sorted(matching_files, key=lambda x: x.last_modified, reverse=True)[0]

        # Step 3: Fetch and load the latest file
        response = minio_client.get_object(bucket_name, latest_file.object_name)
        df = pd.read_parquet(response)

        return df.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve grouped result: {str(e)}")




# @router.get("/results")
# def get_latest_groupby_result():
#     if "grouped_result" not in groupby_store:
#         raise HTTPException(status_code=404, detail="No results available")
    
#     df = groupby_store["grouped_result"]
#     return df.to_dict(orient="records")

