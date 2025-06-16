from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as feature_overview_router

app = FastAPI(title="Feature Overview Validator")


# Register routes
app.include_router(feature_overview_router, prefix="/feature-overview", tags=["Feature Overview"])

