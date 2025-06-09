from fastapi import APIRouter
from app.features.feature_overview.endpoint import router as feature_overview_router

api_router = APIRouter()

api_router.include_router(feature_overview_router)


