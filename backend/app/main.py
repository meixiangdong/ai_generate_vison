from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.db import init_engine_and_create_tables
from app.utils.fs import ensure_storage_dirs
from app.routers.pipeline import router as pipeline_router

app = FastAPI(title="AI Video MVP", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure storage directories and DB tables on startup
@app.on_event("startup")
def on_startup():
    ensure_storage_dirs()
    init_engine_and_create_tables()

# Mount static dirs for outputs, covers, srt
app.mount("/outputs", StaticFiles(directory=settings.OUTPUTS_DIR), name="outputs")
app.mount("/covers", StaticFiles(directory=settings.COVERS_DIR), name="covers")
app.mount("/srt", StaticFiles(directory=settings.SRT_DIR), name="srt")

# Routers
app.include_router(pipeline_router, prefix="/api", tags=["pipeline"])

@app.get("/health")
def health():
    return {"ok": True}

# 模块顶部的导入区域
from pathlib import Path

def ensure_storage_dirs():
    candidates = [
        getattr(settings, "OUTPUTS_DIR", "storage/outputs"),
        getattr(settings, "ASSETS_DIR", "storage/assets"),
        getattr(settings, "SRT_DIR", "storage/srt"),
        getattr(settings, "COVERS_DIR", "storage/covers"),
    ]
    for d in candidates:
        Path(d).mkdir(parents=True, exist_ok=True)

# 请确保这行位于 app.mount(...) 之前
ensure_storage_dirs()

# 你的挂载应当在这里之后执行
# app.mount("/outputs", StaticFiles(directory=settings.OUTPUTS_DIR), name="outputs")