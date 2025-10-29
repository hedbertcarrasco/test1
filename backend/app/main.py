from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="React + FastAPI on OpenShift")

# Allow CORS for local dev and typical OpenShift routes; adjust as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/message")
def read_message():
    return {"message": "Hello from FastAPI on OpenShift!"}
