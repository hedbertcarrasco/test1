from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
import os
import re

app = FastAPI(title="React + FastAPI on OpenShift (BFF)")

# Allow CORS internally if needed (not exposed to public in BFF mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (built frontend). We expect files under ./static after image build
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    # Serve built app at root (index.html) and assets
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="ui")


def get_initial_state() -> dict:
    # Here you can fetch any internal data, aggregate, etc.
    # Example: pull message from internal services, databases, etc.
    return {
        "status": "ok",
        "message": "Hello from FastAPI (BFF) via internal Service!",
    }


def inject_state_into_html(html: str, state: dict) -> str:
    state_json = json.dumps(state)
    script_tag = f"<script>window.__INITIAL_STATE__ = {state_json};</script>"
    # Try known marker first
    if "<!--INITIAL_STATE-->" in html:
        return html.replace("<!--INITIAL_STATE-->", script_tag)
    # Otherwise, try to inject before </head> or </body>
    for closing_tag in ["</head>", "</body>"]:
        if closing_tag in html:
            return html.replace(closing_tag, script_tag + closing_tag)
    # Fallback: append
    return html + script_tag


def load_index_html() -> str:
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        return ""
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/", response_class=HTMLResponse)
async def root(_: Request) -> Response:
    html = load_index_html()
    if not html:
        state = json.dumps(get_initial_state())
        html = f"""
        <!doctype html>
        <html><head><meta charset='utf-8'><title>BFF</title></head>
        <body>
          <script>window.__INITIAL_STATE__ = {state};</script>
          <div id='root'>Build missing. Initial state embedded.</div>
        </body></html>
        """
        return HTMLResponse(content=html)
    return HTMLResponse(content=inject_state_into_html(html, get_initial_state()))


# SPA fallback to index for client-side routes
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(full_path: str) -> Response:
    # Serve index.html for any unmatched path; assets are served via /assets mount
    html = load_index_html()
    if not html:
        return HTMLResponse(content="Not built", status_code=404)
    return HTMLResponse(content=inject_state_into_html(html, get_initial_state()))


# Optional API still available internally/external if needed
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/message")
def read_message():
    return {"message": "Hello from FastAPI on OpenShift!"}
