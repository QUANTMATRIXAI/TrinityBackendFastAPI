# app/routes.py

from fastapi import APIRouter, Form, HTTPException

import json
from .transform.base import calculate_residuals, compute_rpi, apply_stl_outlier

from .deps import get_minio_df,fetch_measures_list,get_column_classifications_collection,get_transform_settings_collection
from .mongodb_saver import save_transform_data,save_tansform_data_settings
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from pykalman import KalmanFilter

router = APIRouter()

import pandas as pd


@router.get("/options")
async def get_transform_options():
    return {
        "transform_operations": [
            "power",
            "log",
            "sqrt",
            "exp",
            "marketshare",
            "kalman_filter",
            "standardize_zscore",
            "standardize_minmax",
            "standardize_none",
            "logistic"
        ]
    }



@router.post("/settings")
async def set_create_options(
    options: str = Form(...),
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    ):

    options = [opt.strip() for opt in options.split(",") if opt.strip()]

    await save_tansform_data_settings(
        collection_name="transform_settings",
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

latest_transform_data: DataFrame | None = None

@router.post("/perform")
async def perform_transform(
    request: Request,
    # object_names: str = Form(...),
    # # file2: str = Form(...),
    # bucket_name: str = Form(...),
    validator_atom_id: str = Form(...),
    file_key: str = Form(...),
    # operation_names: str = Form(...),
    # columns: str = Form(...),  # comma-separated
    # extra_param: str = Form(None)    
):
    global latest_transform_data 
    try:
        # Read CSVs from MinIO
        # df = get_minio_df(bucket_name, object_names)
        df=pd.read_excel("D0.xlsx")
        # df.columns = [col.strip().lower() for col in df.columns]

        df.columns = df.columns.str.strip().str.lower()
        ms_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()



        # Step 1: Fetch expected operation order from MongoDB
        transform_collection = await get_transform_settings_collection()
        doc = await transform_collection.find_one({
            "validator_atom_id": validator_atom_id,
            "file_key": file_key
        })
        if not doc or "operations" not in doc:
            raise HTTPException(status_code=400, detail="No transform settings found in MongoDB")

        expected_operations = doc["operations"]


        # Step 1: Parse all form items preserving duplicates
        form_data = await request.form()
        form_items = list(form_data.multi_items())  # only call this ONCE   

        operation_order = []
        operation_columns = []
        operation_params = []

        # Keep counters per operation to support multiple usages
        param_counter = {}

        for key, value in form_items:
            if key in ["validator_atom_id", "file_key", "options"]:
                continue
            if key.startswith("params_"):
                continue  # Skip param keys here

            # This is a transformation operation
            columns = [col.strip() for col in value.split(",") if col.strip()]
            operation_order.append(key)
            operation_columns.append(columns)

            # Handle param for this op (if exists)
            param_key = f"params_{key}"
            param_counter[key] = param_counter.get(key, 0) + 1

            # Get N-th param value for this op
            param_values = [v for k, v in form_items if k == param_key]
            param = param_values[param_counter[key] - 1] if len(param_values) >= param_counter[key] else None
            operation_params.append(param)


        # Step 3: Validate order and count
        if operation_order != expected_operations:
            raise HTTPException(
                status_code=400,
                detail=f"Input operations {operation_order} do not match expected order {expected_operations}"
            )

        # Step 4: Run operations
        new_cols_all = []
        operation_details = []

        for i, op in enumerate(operation_order):
            columns = operation_columns[i]
            param = operation_params[i]
            new_cols = []

            # Store operation metadata
            operation_details.append({
                "operation": op,
                "columns": columns,
                "params": param
            })

            if op == 'power':
                if param is None:
                    raise HTTPException(status_code=400, detail="Missing `param` for power operation")
                try:
                    exponent = float(param)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid exponent: {param}")

                for col in columns:
                    if col not in ms_cols:
                        raise ValueError(f"Column {col} not a valid measure")
                    new_col = f"{col}_power{param}"
                    df[new_col] = df[col] ** exponent
                    new_cols.append(new_col)

            # --- Log ---
            elif op == 'log':
                for col in columns:
                    new_col = f"{col}_log"
                    df[new_col] = np.log(df[col])
                    new_cols.append(new_col)

            # --- Sqrt ---
            elif op == 'sqrt':
                for col in columns:
                    new_col = f"{col}_sqrt"
                    df[new_col] = np.sqrt(df[col])
                    new_cols.append(new_col)

            # --- Exp ---
            elif op == 'exp':
                for col in columns:
                    new_col = f"{col}_exp"
                    df[new_col] = np.exp(df[col])
                    new_cols.append(new_col)

            # --- Marketshare ---
            elif op == 'marketshare':
                d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
                d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
                if not d_date:
                    raise ValueError("Date column not found in data.")
                catvol = df.groupby([d_channel, d_date])['Volume'].sum().reset_index(name='CatVol')
                df = df.merge(catvol, on=[d_channel, d_date], how='left')
                df['NetCatVol'] = df['CatVol'] - df['Volume']
                keys_for_brand = [d_channel] + columns
                brand_totals = df.groupby(keys_for_brand)['SalesValue'].sum().reset_index(name='BrandSales')
                channel_totals = df.groupby(d_channel)['SalesValue'].sum().reset_index(name='ChannelSales')
                brand_totals = brand_totals.merge(channel_totals, on=[d_channel], how='left')
                brand_totals['MarketShare_overall'] = (brand_totals['BrandSales'] / brand_totals['ChannelSales'] * 100).fillna(0)
                df = df.merge(brand_totals[[*keys_for_brand, 'MarketShare_overall']], on=keys_for_brand, how='left')
                new_cols.append('MarketShare_overall')

            # --- Kalman Filter ---
            elif op == 'kalman_filter':
                d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
                d_channel = next((c for c in df.columns if c.strip().lower() == 'channel'), 'Channel')
                df[d_date] = pd.to_datetime(df[d_date], errors='coerce')
                final_df = df.copy().sort_values(by=d_date).set_index(d_date)
                final_df['FilteredVolume'] = np.nan

                def apply_kf(vals):
                    kf = KalmanFilter(initial_state_mean=vals[0], n_dim_obs=1)
                    means, _ = kf.filter(vals)
                    return means.flatten()

                for _, grp in final_df.groupby([d_channel] + (columns or [])):
                    grp_s = grp.sort_values(by=d_date).reset_index()
                    try:
                        filt = apply_kf(grp_s['Volume'].values)
                        final_df.loc[grp_s['index'], 'FilteredVolume'] = filt
                    except:
                        continue

                if 'CatVol' in final_df.columns:
                    final_df['FilteredVolume'] = np.where(final_df['CatVol'] != 0,
                                                        final_df['FilteredVolume'] / final_df['CatVol'], 0)
                df = final_df.reset_index()
                new_cols.append('FilteredVolume')

            # --- Standardization ---
            elif op.startswith('standardize'):
                method = op.split("_")[1]  # zscore / minmax / none
                if method == 'zscore':
                    scaler = StandardScaler()
                elif method == 'minmax':
                    scaler = MinMaxScaler()
                elif method == 'none':
                    scaler = None
                else:
                    raise ValueError("Unknown standardization method")

                for col in columns:
                    new_col = f"{col}_scaled"
                    df[new_col] = scaler.fit_transform(df[[col]]) if scaler else df[col]
                    new_cols.append(new_col)

            # --- Logistic ---
            elif op == 'logistic':
                import json

                def adstock_function(series, carryover):
                    result, prev = [], 0
                    for val in series:
                        curr = val + carryover * prev
                        result.append(curr)
                        prev = curr
                    return np.array(result)

                def logistic_function(x, gr, mp):
                    return 1 / (1 + np.exp(-gr * (x - mp)))

                logistic_params = json.loads(param)
                gr = logistic_params.get("gr")
                co = logistic_params.get("co")
                mp = logistic_params.get("mp")
                if gr is None or co is None or mp is None:
                    raise ValueError("Missing logistic parameters")

                for col in columns:
                    adstocked = adstock_function(df[col].fillna(0), co)
                    standardized = (adstocked - np.mean(adstocked)) / np.std(adstocked)
                    df[f"{col}_logistic"] = logistic_function(standardized, gr, mp)
                    new_cols.append(f"{col}_logistic")

            # --- Seasonality + Trend ---
            elif op == 'seasonality_trend':
                d_date = next((c for c in df.columns if c.strip().lower() == 'date'), None)
                if not d_date:
                    raise ValueError("Date column not found in data")
                df[d_date] = pd.to_datetime(df[d_date], errors='coerce')
                df.sort_values(by=d_date, inplace=True)

                from statsmodels.tsa.seasonal import STL
                for col in columns:
                    stl = STL(df[col].fillna(method='ffill'), seasonal=13)
                    res = stl.fit()
                    df[f"{col}_seasonality"] = res.seasonal
                    df[f"{col}_trend"] = res.trend
                    new_cols.extend([f"{col}_seasonality", f"{col}_trend"])

            # Add all new cols to master list
            new_cols_all.extend(new_cols)


        latest_transform_data = df


        await save_transform_data(
            collection_name="transform_results",
            data={
                "validator_atom_id": validator_atom_id,
                "file_key": file_key,
                "operations_performed": operation_details
                # "result": df_transformed.to_dict(orient="records")  # optional
            }
        )



        return {"status": "SUCCESS", "new_columns": new_cols_all}

    
    
    except Exception as e:
        return {"status": "FAILURE", "error": str(e)}


    

import numpy as np
@router.get("/results")
async def get_create_data():
    global latest_transform_data
    if latest_transform_data is None:
        raise HTTPException(status_code=404, detail="No create data available yet.")
    

    sanitized_data = latest_transform_data.replace({np.nan: None, np.inf: None, -np.inf: None})
       
    return {
        # "row_count": len(latest_renamed_data),
        "transform_data": sanitized_data.to_dict(orient="records")
    }
