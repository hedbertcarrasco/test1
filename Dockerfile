# syntax=docker/dockerfile:1

# Build frontend using Red Hat UBI Node.js 20
FROM registry.access.redhat.com/ubi9/nodejs-20:latest AS web-build
WORKDIR /app/frontend
# Ensure devDependencies are installed (Vite)
ENV NODE_ENV=development \
    NPM_CONFIG_PRODUCTION=false
COPY frontend/package.json frontend/package-lock.json* frontend/pnpm-lock.yaml* frontend/yarn.lock* ./
RUN if [ -f package-lock.json ]; then npm ci --omit=dev=false; \
    elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i --frozen-lockfile; \
    elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    else npm i; fi
COPY frontend/ .
RUN npm run build

# Backend runtime image using Red Hat UBI Python 3.11
FROM registry.access.redhat.com/ubi9/python-311:latest AS api
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# Install backend deps
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend app
COPY backend/app /app/app

# Copy built frontend to app static directory
RUN mkdir -p /app/app/static
COPY --from=web-build /app/frontend/dist/ /app/app/static/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
