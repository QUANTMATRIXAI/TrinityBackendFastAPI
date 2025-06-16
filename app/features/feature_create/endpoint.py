# app/features/feature_overview/endpoint.py

from fastapi import APIRouter
from .routes import router as create_routes

router = APIRouter()
router.include_router(
    create_routes,
    prefix="/create",
    tags=["create"]
)
