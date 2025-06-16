from fastapi import FastAPI
from .routes import router as transform_router

app = FastAPI(title="Transform Atom")
app.include_router(transform_router,prefix="/transform", tags=["transform"])
