from fastapi import FastAPI
from api.insta import router

app = FastAPI()
app.include_router(router)