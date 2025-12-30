from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.api.routes import router
from fastapi import FastAPI


app = FastAPI(title="Email Generator API")

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}
app.include_router(router)
