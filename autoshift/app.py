from __future__ import annotations

import os

# Set before importing the browser library; Auto Shift does not record model logs.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "false")
os.environ.setdefault("BROWSER_USE_SETUP_LOGGING", "false")
os.environ.setdefault("BROWSER_USE_LOGGING_LEVEL", "critical")
os.environ.setdefault("DO_NOT_TRACK", "1")

import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .engine import Decision, SessionConfig, TaskConfig, Workspace

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
TOKEN = secrets.token_urlsafe(32)
workspace = Workspace()
logging.getLogger("browser_use").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app):
    yield
    await workspace.close_browser()


app = FastAPI(title="Auto Shift", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])


@app.middleware("http")
async def protect(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        supplied = request.headers.get("x-autoshift-token", "")
        origin = request.headers.get("origin")
        if not secrets.compare_digest(supplied, TOKEN):
            return JSONResponse({"detail": "Open the private launch link from your terminal."}, status_code=401)
        if origin and origin not in {"http://127.0.0.1:8765", "http://localhost:8765"}:
            return JSONResponse({"detail": "Cross-origin requests are not allowed."}, status_code=403)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
        "base-uri 'none'; form-action 'self'"
    )
    return response


@app.exception_handler(RequestValidationError)
async def invalid_input(request, exc):
    # Do not echo rejected inputs; a rejected field may contain an API key.
    return JSONResponse({"detail": "Check your task, model, step limit and exact website hostnames."}, status_code=422)


@app.get("/")
async def home():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/state")
async def state():
    return workspace.snapshot()


@app.post("/api/browser")
async def open_browser(config: SessionConfig):
    try:
        await workspace.open_browser(config)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    except Exception:
        raise HTTPException(503, "Browser could not start. Run setup and use a desktop session with Chromium installed.")
    return workspace.snapshot()


@app.post("/api/tasks")
async def start_task(config: TaskConfig):
    try:
        await workspace.start_task(config)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    except Exception:
        raise HTTPException(503, "The agent could not start. Check your installed dependencies and model settings.")
    return {"status": "started"}


@app.post("/api/decision")
async def decision(value: Decision):
    try:
        workspace.decide(value)
    except ValueError as exc:
        raise HTTPException(409, str(exc))
    return {"status": "accepted"}


@app.post("/api/stop")
async def stop():
    await workspace.stop_task()
    return {"status": "stopped"}


@app.post("/api/close")
async def close():
    await workspace.close_browser()
    return {"status": "closed"}


app.mount("/static", StaticFiles(directory=ROOT / "web"), name="static")
