# Stage 1: Build frontend assets
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Set npm registry to official registry and install dependencies (including devDependencies for build)
RUN npm config set registry https://registry.npmjs.org/ && \
    npm ci

# Copy frontend source
COPY frontend/ ./

# Create output directory structure and build frontend assets
RUN mkdir -p ../blog/static/blog/dist && \
    npm run build

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
COPY --from=frontend-builder /blog/static/blog/dist /code/djangoblog/blog/static/blog/dist

# Set execute permission for entrypoint
RUN chmod +x /code/djangoblog/deploy/entrypoint.sh

ENTRYPOINT ["/code/djangoblog/deploy/entrypoint.sh"]
