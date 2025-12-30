from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Email Generator API")
app.include_router(router)
