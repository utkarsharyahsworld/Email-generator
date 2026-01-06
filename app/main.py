from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router

app = FastAPI(title="Email Generator API")

# 1. Mount the 'static' folder
# This lets the browser access files inside app/static/
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 2. Include your API routes
app.include_router(router)

# 3. Serve the UI at the root URL ("/")
@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}