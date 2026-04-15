import os
from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from db.database import Base, engine
from models.deal import Deal
from routes import chat, deals

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    print("Starting up — creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables ready.")
    yield
    # Shutdown
    print("Shutting down.")

app = FastAPI(title="AI Sales Simulator", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        print(f"→ {response.status_code}")
        return response
    except Exception as e:
        print(f"→ ERROR: {e}")
        raise

os.makedirs("frontend", exist_ok=True)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.include_router(chat.router, prefix="")
app.include_router(deals.router, prefix="")

@app.get("/")
async def root():
    return {"message": "Deal AI API running", "docs": "/docs"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"UNHANDLED EXCEPTION: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": str(exc)})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
