from fastapi import APIRouter
from app.features.feature_overview.endpoint import router as feature_overview_router
from app.features.text_box.textboxapp.routes import router as textbox_router
from app.features.chart_maker.Chart_Maker_API.app.routes import router as chart_router

api_router = APIRouter()
text_router  = APIRouter()
chart_maker_router = APIRouter()
api_router.include_router(feature_overview_router)
text_router.include_router(textbox_router)
chart_maker_router.include_router(chart_router)

