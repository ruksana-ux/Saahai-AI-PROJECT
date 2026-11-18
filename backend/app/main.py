"""
Read-only scheme dataset service.

This service does not see images, document text, or user profiles. The Android
client does not call it in this release; it exists for a future, user-initiated
citation refresh that falls back to the bundled asset. Core features work without
it.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = Path(
    os.getenv("SAHAAYA_DATASET", str(REPO_ROOT / "data" / "schemes" / "schemes.json"))
)

app = FastAPI(
    title="Sahaaya Drishti dataset service",
    version="1.0.0",
    description="Read-only, citation-backed scheme dataset. No user data is accepted.",
)

_allowed_origins = [
    origin.strip()
    for origin in os.getenv("SAHAAYA_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if _allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins,
        allow_methods=["GET"],
        allow_headers=["If-None-Match"],
    )


def _load() -> Dict[str, Any]:
    with DATASET_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _etag(payload: bytes) -> str:
    return '"' + hashlib.sha256(payload).hexdigest()[:32] + '"'


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@app.get("/health")
def health() -> Dict[str, Any]:
    try:
        data = _load()
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail=f"dataset unavailable: {exc}") from exc
    return {
        "status": "ok",
        "dataset_version": data.get("dataset_version"),
        "last_verified": data.get("last_verified"),
        "records": len(data.get("schemes", [])),
    }


@app.get("/v1/schemes")
def list_schemes(request: Request, response: Response, category: Optional[str] = None) -> Any:
    payload = DATASET_PATH.read_bytes()
    tag = _etag(payload)
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304)

    data = _load()
    schemes: List[Dict[str, Any]] = data.get("schemes", [])
    if category:
        schemes = [scheme for scheme in schemes if scheme.get("category") == category]

    response.headers["ETag"] = tag
    return {
        "dataset_version": data.get("dataset_version"),
        "last_verified": data.get("last_verified"),
        "schemes": [
            {
                "id": scheme["id"],
                "name": scheme["name"],
                "category": scheme["category"],
                "summary": scheme["summary"],
                "last_verified": scheme["last_verified"],
                "review_due": scheme["review_due"],
                "verification_status": scheme["verification_status"],
            }
            for scheme in schemes
        ],
    }


@app.get("/v1/schemes/{scheme_id}")
def get_scheme(scheme_id: str, request: Request, response: Response) -> Any:
    payload = DATASET_PATH.read_bytes()
    tag = _etag(payload)
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304)

    data = _load()
    for scheme in data.get("schemes", []):
        if scheme["id"] == scheme_id:
            response.headers["ETag"] = tag
            return scheme

    raise HTTPException(status_code=404, detail="scheme not found")


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    # Never leak a stack trace to a client.
    return JSONResponse(status_code=500, content={"detail": "internal error"})
