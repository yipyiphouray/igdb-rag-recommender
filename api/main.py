from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

API_DIR = Path(__file__).resolve().parent
ROOT_DIR = API_DIR.parent

for path in (API_DIR, ROOT_DIR):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from app.routers import catalog, health, insights, methodology, recommendations  # noqa: E402


app = FastAPI(
    title="IGDB Game Discovery API",
    description="Backend API for the final IGDB game discovery website.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(recommendations.router)
app.include_router(methodology.router)
app.include_router(insights.router)
