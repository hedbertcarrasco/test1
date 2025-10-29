from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import json
import os

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
    app.mount("/assets", StaticFiles(directory=static_dir), name="assets")


def get_initial_state() -> dict:
    # Here you can fetch any internal data, aggregate, etc.
    # Example: pull message from internal services, databases, etc.
    return {
        "status": "ok",
        "message": "Hello from FastAPI (BFF) via internal Service!",
    }


@app.get("/", response_class=HTMLResponse)
async def index(_: Request) -> Response:
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        # Fallback minimal page if static build is missing
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

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    state_json = json.dumps(get_initial_state())
    injection = f"<script>window.__INITIAL_STATE__ = {state_json};</script>"
    html = html.replace("<!--INITIAL_STATE-->", injection)
    return HTMLResponse(content=html)


# Optional API still available internally/external if needed
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/message")
def read_message():
    return {"message": "Hello from FastAPI on OpenShift!"}
