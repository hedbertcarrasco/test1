from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI(title="React + FastAPI on OpenShift (BFF)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    # Serve built assets at /assets
    app.mount("/assets", StaticFiles(directory=static_dir), name="assets")


def get_initial_state() -> dict:
    return {
        "status": "ok",
        "message": "Hello from FastAPI (BFF) via internal Service!",
    }


def load_index_html() -> str:
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        return ""
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()


def inject_state(html: str, state: dict) -> str:
    state_json = json.dumps(state)
    script_tag = f"<script>window.__INITIAL_STATE__ = {state_json};</script>"
    if "<!--INITIAL_STATE-->" in html:
        return html.replace("<!--INITIAL_STATE-->", script_tag)
    # inject before </head> or </body>
    for tag in ("</head>", "</body>"):
        if tag in html:
            return html.replace(tag, script_tag + tag)
    return html + script_tag


@app.get("/", response_class=HTMLResponse)
async def root(_: Request) -> Response:
    html = load_index_html()
    if not html:
        return HTMLResponse("Build missing", status_code=503)
    return HTMLResponse(inject_state(html, get_initial_state()))


@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_fallback(full_path: str) -> Response:
    # Serve index for client routes; real assets are under /assets
    html = load_index_html()
    if not html:
        return HTMLResponse("Not found", status_code=404)
    return HTMLResponse(inject_state(html, get_initial_state()))


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/message")
def read_message():
    return {"message": "Hello from FastAPI on OpenShift!"}
