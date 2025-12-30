# Stage 1: Build frontend assets
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy frontend package files
COPY frontend/package*.json ./frontend/

# Set npm registry to official registry and install dependencies (including devDependencies for build)
RUN cd frontend && \
    npm config set registry https://registry.npmjs.org/ && \
    npm ci

# Copy frontend source and blog directory structure
COPY frontend/ ./frontend/
COPY blog/static/blog/ ./blog/static/blog/

# Build frontend assets (output goes to blog/static/blog/dist)
RUN cd frontend && npm run build

# Stage 2: Build final image
FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /code/djangoblog/

# Install system dependencies
RUN apt-get update && \
    apt-get install default-libmysqlclient-dev gettext -y && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn[gevent] && \
    pip cache purge

# Copy application code
COPY . .

# Copy built frontend assets from frontend-builder stage
COPY --from=frontend-builder /app/blog/static/blog/dist /code/djangoblog/blog/static/blog/dist

# Set execute permission for entrypoint
RUN chmod +x /code/djangoblog/deploy/entrypoint.sh

ENTRYPOINT ["/code/djangoblog/deploy/entrypoint.sh"]
