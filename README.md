# React + FastAPI on OpenShift

This is a minimal example showing a React frontend (Vite) and a FastAPI backend, containerized and ready for OpenShift.

## Local development

Backend:

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm install
# Optionally point to a different API (defaults to http://localhost:8000)
# export VITE_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173 and you should see the page, with the API message from FastAPI.

## Container builds (optional local)

Backend:

```bash
cd backend
docker build -t demo/backend:latest .
```

Frontend (optionally set API URL at build time):

```bash
cd frontend
# Example using a public route to backend
# docker build --build-arg VITE_API_URL=https://your-backend-route/ -t demo/frontend:latest .
docker build -t demo/frontend:latest .
```

## Deploy to OpenShift (template)

The repo includes an OpenShift Template at `openshift/template.yaml` that defines:
- ImageStreams and Docker BuildConfigs for backend and frontend (building from this Git repo)
- Deployments, Services, and Routes for both components

You will need:
- An OpenShift project selected (e.g., `oc project my-project`)
- This repository accessible by the OpenShift cluster (public or reachable via webhook/credentials)

Process and apply the template:

```bash
# Required: set your Git repository URL
GIT_URI="https://github.com/your-org/your-repo.git"
# Optional: branch/ref
git_ref="main"
# Optional: Inject API URL into frontend build (otherwise the app will try same host:8000)
# For example, after the backend route is created, you can re-build with that host
vite_api_url=""

oc process -f openshift/template.yaml \
  -p NAME=react-fastapi \
  -p NAMESPACE=$(oc project -q) \
  -p GIT_URI="$GIT_URI" \
  -p GIT_REF="$git_ref" \
  -p VITE_API_URL="$vite_api_url" \
| oc apply -f -
```

Start the builds (if not auto-triggered):

```bash
oc start-build react-fastapi-backend --wait
oc start-build react-fastapi-frontend --wait
```

Once images are built, OpenShift will deploy them. Get the routes:

```bash
oc get routes
```

- The backend exposes `/api/health` and `/api/message`.
- The frontend is a static site served on port 8080.

### Common adjustments
- CORS: The backend currently allows `*` for simplicity; in production, restrict origins.
- Frontend API URL: Provide `VITE_API_URL` at build time to point to your backend route, e.g., `https://react-fastapi-backend-<ns>.<cluster-domain>`.
- Scaling: Update replicas in the Deployments as needed.
# test1
