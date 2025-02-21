from fastapi import FastAPI

from .api.db import init_db
from .api.main.views import api_router as main_router

app = FastAPI()

app.mount("", main_router)

init_db()
