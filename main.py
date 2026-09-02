"""
main.py
FastAPI entry point for the Render deployable dashboard project.

Endpoints:
    GET /health     -> simple health check for uptime monitors / Render
    GET /dashboard  -> renders all JSON datasets as HTML tables via Jinja2
    GET /            -> redirects to /dashboard for convenience
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"
TEMPLATES_DIR = BASE_DIR / "templates"

USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

app = FastAPI(
    title="Ops Dashboard API",
    description="A lightweight FastAPI dashboard that renders JSON datasets as tables.",
    version="1.0.0",
)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount a static dir only if it exists (kept optional, safe for Render)
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Friendly labels for each dataset file, shown as panel titles on the dashboard
DATASET_LABELS = {
    "gps_tracker": "GPS Tracker",
    "weather": "Weather",
    "delay_patterns": "Delay Patterns",
    "congestion": "Congestion",
    "signal_aspects": "Signal Aspects",
    "station_ops": "Station Operations",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_dataset(filename: str):
    """Load a single JSON dataset file from the datasets/ directory.

    Returns a list of dict rows (or an empty list if the file is missing
    or invalid, so the dashboard never crashes on a bad/absent file).
    """
    file_path = DATASETS_DIR / filename
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Normalize to a list of rows
        if isinstance(data, dict):
            data = data.get("data", data.get("rows", [data]))
        if not isinstance(data, list):
            data = [data]
        return data
    except (json.JSONDecodeError, OSError):
        return []


def load_all_panels():
    """Load every known dataset and build the panel structure the template needs.

    Each panel is a dict: {"key", "title", "columns", "rows"}.
    """
    panels = []
    for key, title in DATASET_LABELS.items():
        rows = load_dataset(f"{key}.json")
        columns = list(rows[0].keys()) if rows else []
        panels.append(
            {
                "key": key,
                "title": title,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
            }
        )
    return panels


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    """Redirect the root path to the dashboard for convenience."""
    return RedirectResponse(url="/dashboard")


@app.get("/health")
def health_check():
    """Simple health check endpoint used by Render / uptime monitors."""
    return JSONResponse(
        {
            "status": "ok",
            "use_mock_data": USE_MOCK_DATA,
            "datasets_available": [
                f"{key}.json" for key in DATASET_LABELS.keys()
                if (DATASETS_DIR / f"{key}.json").exists()
            ],
        }
    )


@app.get("/dashboard")
def dashboard(request: Request):
    """Render the dashboard page: loops over all JSON datasets and shows
    each as a table panel."""
    panels = load_all_panels()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "panels": panels,
            "use_mock_data": USE_MOCK_DATA,
            "title": "Operations Dashboard",
        },
    )


# ---------------------------------------------------------------------------
# Local dev entry point (Render uses the Start Command instead)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
