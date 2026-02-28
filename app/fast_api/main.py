from fastapi import FastAPI
from app.fast_api.credits import router

app = FastAPI()
app.include_router(router)
