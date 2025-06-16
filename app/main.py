# from fastapi import FastAPI
# from app.api.router import api_router

# app = FastAPI()

# app.include_router(api_router)

from fastapi import FastAPI
from app.api.router import api_router, text_router, chart_maker_router,validate_router

app = FastAPI()

app.include_router(api_router, prefix="/api")
app.include_router(text_router, prefix="/api/t")
app.include_router(chart_maker_router, prefix="/api/filter_charts")
app.include_router(validate_router, prefix="/validator_atom")