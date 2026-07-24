from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parent
ROOT_DIR = API_DIR.parent

load_dotenv(ROOT_DIR / ".env")

for path in (API_DIR, ROOT_DIR):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

from app.routers import catalog, chat, health, insights, methodology, recommendations  # noqa: E402


LOCAL_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


def _cors_origins() -> list[str]:
    """Return allowed browser origins for local and deployed frontends.

    Deployment usage:
    - FRONTEND_ORIGIN=https://your-site.vercel.app
    - CORS_ALLOWED_ORIGINS=https://site-one.vercel.app,https://site-two.vercel.app
    """
    configured_origins = []
    for env_name in ("FRONTEND_ORIGIN", "CORS_ALLOWED_ORIGINS"):
        raw_value = os.getenv(env_name, "")
        configured_origins.extend(
            origin.strip().rstrip("/")
            for origin in raw_value.split(",")
            if origin.strip()
        )

    origins = [*LOCAL_CORS_ORIGINS, *configured_origins]
    return list(dict.fromkeys(origins))


app = FastAPI(
    title="IGDB Game Discovery API",
    description="Backend API for the final IGDB game discovery website.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(catalog.router)
app.include_router(recommendations.router)
app.include_router(chat.router)
app.include_router(methodology.router)
app.include_router(insights.router)
