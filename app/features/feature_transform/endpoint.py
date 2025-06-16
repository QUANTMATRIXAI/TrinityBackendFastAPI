# app/features/feature_overview/endpoint.py

from fastapi import APIRouter
from .routes import router as transform_routes

router = APIRouter()
router.include_router(
    transform_routes,
    prefix="/transform",
    tags=["transform"]
)
