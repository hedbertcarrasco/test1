# React + FastAPI on OpenShift (BFF)

FastAPI sirve el build de React y embebe el estado inicial: el navegador nunca llama al backend directamente; todas las llamadas internas ocurren dentro del clúster.

## Local development

Backend (incluye servir el build, si existe):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Inicia FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (para construir assets):

```bash
cd frontend
npm install
npm run build
# Esto genera dist/; al construir la imagen se copiará a backend/app/static
```

Abre http://localhost:8000 para ver la app (si ya copiaste dist a backend/app/static).

## Imagen única (Docker)

Construye desde la raíz (Dockerfile unificado):

```bash
docker build -t demo/react-fastapi-bff:latest .
```

## OpenShift (un solo BuildConfig/Deployment)

- Plantilla: `openshift/template.yaml` crea un BuildConfig desde la raíz del repo, una ImageStream, un Deployment, un Service y un Route.

Procesa y aplica:

```bash
oc process -f openshift/template.yaml \
  -p NAME=react-fastapi \
  -p NAMESPACE=$(oc project -q) \
  -p GIT_URI="https://github.com/hedbertcarrasco/test1.git" \
  -p GIT_REF="main" \
| oc apply -f -
```

Lanza el build y espera:

```bash
oc start-build react-fastapi --wait --follow
```

Reinicia el despliegue si ya existía:

```bash
oc rollout restart deploy/react-fastapi
oc rollout status deploy/react-fastapi
```

Obtén la URL pública:

```bash
oc get route react-fastapi -o jsonpath='{.spec.host}{"\n"}'
```

### Notas
- Arquitectura BFF: el HTML incluye `window.__INITIAL_STATE__` generado en el servidor; React no hace fetch en el cliente.
- Backend interno: cualquier integración adicional se realiza desde FastAPI hacia Services internos.
- Seguridad: no necesitas exponer el backend por separado; el Route público apunta solo al BFF (FastAPI).
