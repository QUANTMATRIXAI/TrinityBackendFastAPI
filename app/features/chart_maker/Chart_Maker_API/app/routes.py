from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import pandas as pd
from .schemas import ChartRequest
from .chart_service import create_chart
import json
from app.features.chart_maker.Chart_Maker_API.app.schemas import CategoricalFilter, NumericalFilter
from .miniodb import get_object, put_object
from fastapi import APIRouter, Form, HTTPException, Query
from app.features.chart_maker.Chart_Maker_API.Filters.datafilter import filter_and_store, CategoricalFilter, NumericalFilter
from app.features.chart_maker.Chart_Maker_API.Filters.providing_data_for_filter import get_filter_metadata_with_unique
import io
from minio import Minio
router = APIRouter()

@router.get("/columns")
def get_chart_columns(
    bucket: str = Query(...),
    object_name: str = Query(...)
):
    try:
        file_bytes = get_object(bucket, object_name)
        df = pd.read_csv(io.BytesIO(file_bytes))
        return {"columns": df.columns.tolist()}
    except Exception as e:
        raise HTTPException(500, detail=f"Could not read columns: {str(e)}")


@router.get("/filter/metadata")
def filter_metadata(
    bucket: str = Query(...),
    object_name: str = Query(...)
):
    try:
        csv_bytes = get_object(bucket, object_name)
        df = pd.read_csv(pd.io.common.BytesIO(csv_bytes))
        metadata = get_filter_metadata_with_unique(df)
        return metadata
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    

@router.post("/filter")
async def filter_data(
    bucket: str = Form(...),
    object_name: str = Form(...),
    filters: str = Form(...)
):
    try:
        # Get file bytes from MinIO
        file_bytes = get_object(bucket, object_name)
        file_stream = io.BytesIO(file_bytes)
        if object_name.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_stream)
        else:
            df = pd.read_csv(file_stream)
        filters_list = json.loads(filters)
        filter_objs = []
        for f in filters_list:
            if f["type"] == "categorical":
                filter_objs.append(CategoricalFilter(**f))
            elif f["type"] == "numerical":
                filter_objs.append(NumericalFilter(**f))

        filtered_df, metadata = await filter_and_store(df, filter_objs, bucket, object_name)

        return {
            "matched_count": len(filtered_df),
            "minio_object": metadata["object_name"],
            "message": "Filtered CSV saved and metadata stored"
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))



@router.post("/chart")
async def generate_chart(
    bucket: str = Form(...),
    object_name: str = Form(...),
    config: str = Form(...)
):
    try:
        csv_bytes = get_object(bucket, object_name)
        df = pd.read_csv(io.BytesIO(csv_bytes))
        data = df.to_dict(orient="records")
        config_obj = json.loads(config)
        print("About to call generate_chart")
        chart_req = ChartRequest(**config_obj)
        print(chart_req.chart_type)
        fig = create_chart(chart_req, data)
        print("generate_chart returned")
        return {"chart": fig.to_json()}
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid chart config JSON")
    except pd.errors.ParserError:
        raise HTTPException(400, "Invalid CSV file")
    except Exception as e:
        raise HTTPException(500, f"Chart generation failed: {str(e)}")
