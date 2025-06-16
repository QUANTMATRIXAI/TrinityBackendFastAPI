# app/routes.py

from fastapi import APIRouter, Form, HTTPException

import json
from .create.base import calculate_residuals, compute_rpi, apply_stl_outlier

from .deps import get_minio_df,fetch_measures_list,get_column_classifications_collection,get_create_settings_collection
from .mongodb_saver import save_create_data,save_create_data_settings

router = APIRouter()

import pandas as pd



CREATE_OPTIONS = {
    "add",
    "subtract",
    "multiply",
    "divide",
    "residual",
    "dummy",
    "seasonality",
    "trend",
    "rpi"
}

@router.get("/options")
async def get_create_options():
    return {"status": "SUCCESS", "available_create_operations": CREATE_OPTIONS}


@router.post("/settings")
async def set_create_options(
    options: str = Form(...),
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    ):

    options = [opt.strip() for opt in options.split(",") if opt.strip()]

    await save_create_data_settings(
        collection_name="create_settings",
        data={
            "validator_atom_id": validator_atom_id,
            "file_key": file_key,
            "operations": options
            # "result": df_transformed.to_dict(orient="records")  # optional
        }
    )

    return {"status": "SUCCESS", "message": "Options updated", "current_options": options}



from pandas import DataFrame
from typing import List
# from fastapi import Request
from starlette.requests import Request

latest_create_data: DataFrame | None = None

@router.post("/perform")
async def perform_transform(
    request: Request,
    object_names: str = Form(...),
    # # file2: str = Form(...),
    bucket_name: str = Form(...),
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    # operation_names: str = Form(...),
    # columns: str = Form(...),  # comma-separated
    # extra_param: str = Form(None)    
):
    global latest_create_data 
    try:
        # Read CSVs from MinIO
        df = get_minio_df(bucket_name, object_names)


        df.columns = df.columns.str.strip().str.lower()
        form_data = await request.form()
        # operation_list = list(form_data.keys())



        operation_list = []
        operation_columns = []

        for key, value in form_data.multi_items():
            if key in ["validator_atom_id", "file_key","options"]:
                continue
            operation_list.append(key)
            operation_columns.append(value.split(","))

        collection = await get_create_settings_collection()
        settings_doc = await collection.find_one({
            "validator_atom_id": validator_atom_id,
            "file_key": file_key
        })
        if not settings_doc:
            raise HTTPException(status_code=404, detail="Settings not found")

        expected_operations = settings_doc.get("operations", [])

        # Compare as-is including duplicates and order
        if operation_list != expected_operations:
            raise HTTPException(
                status_code=400,
                detail=f"Input operations {operation_list} do not match expected order {expected_operations}."
            )



        new_cols_total = []

        for op, col_str in form_data.multi_items():
            if op in ["validator_atom_id", "file_key","options"]:
                continue

            columns = col_str.split(",")

            # ADD
            if op == "add":
                new_col = "_plus_".join(columns)
                df[new_col] = df[columns].sum(axis=1)
                new_cols_total.append(new_col)

            # SUBTRACT
            elif op == "subtract":
                new_col = "_minus_".join(columns)
                result = df[columns[0]]
                for col in columns[1:]:
                    result -= df[col]
                df[new_col] = result
                new_cols_total.append(new_col)

            # MULTIPLY
            elif op == "multiply":
                new_col = "_times_".join(columns)
                result = df[columns[0]]
                for col in columns[1:]:
                    result *= df[col]
                df[new_col] = result
                new_cols_total.append(new_col)

            # DIVIDE
            elif op == "divide":
                new_col = "_dividedby_".join(columns)
                result = df[columns[0]]
                for col in columns[1:]:
                    result /= df[col]
                df[new_col] = result
                new_cols_total.append(new_col)

            # RESIDUAL
            elif op == "residual":
                y_var = columns[0]
                x_vars = columns[1:]
                residuals, rsq = calculate_residuals(df, y_var, x_vars)
                new_col = f"Res_{y_var}"
                df[new_col] = residuals
                new_cols_total.append(new_col)

            # DUMMY
            elif op == "dummy":
                for col in columns:
                    new_col = f"{col}_dummy"
                    df[new_col] = pd.Categorical(df[col]).codes
                    new_cols_total.append(new_col)

            # RPI
            elif op == "rpi":
                df, rpi_cols = compute_rpi(df, columns)
                new_cols_total.extend(rpi_cols)

            # STL OUTLIER
            elif op == "stl_outlier":
                df, outlier_col = apply_stl_outlier(df, columns)
                new_cols_total.append(outlier_col)

            else:
                raise ValueError(f"Unsupported operation: {op}")
            


            
        latest_create_data = df


        # Collect all operation-column mappings with support for duplicates
        operation_details = []
        for op, col_str in form_data.multi_items():
            if op in ["validator_atom_id", "file_key","options"]:
                continue
            columns = [col.strip() for col in col_str.split(",")]
            operation_details.append({
                "operation": op,
                "columns": columns
            })

        # Save to MongoDB
        await save_create_data(
            collection_name="create_results",
            data={
                "validator_atom_id": validator_atom_id,
                "file_key": file_key,
                "operations_performed": operation_details
                # "result": df_transformed.to_dict(orient="records")  # optional
            }
        )



        return {"status": "SUCCESS", "new_columns": new_cols_total}

    
        
      
    
    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}


    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))


import numpy as np
@router.get("/results")
async def get_create_data():
    global latest_create_data
    if latest_create_data is None:
        raise HTTPException(status_code=404, detail="No create data available yet.")
    

    sanitized_data = latest_create_data.replace({np.nan: None, np.inf: None, -np.inf: None})
       
    return {
        # "row_count": len(latest_renamed_data),
        "created_data": sanitized_data.to_dict(orient="records")
    }
