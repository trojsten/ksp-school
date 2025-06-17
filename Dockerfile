# Frontend builder
FROM node:23-alpine AS frontend-build

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && \
    pnpm install

COPY school ./school
COPY css ./css
COPY tailwind.config.js ./tailwind.config.js
RUN pnpm run build && pnpm run build-js
CMD ["pnpm", "run", "dev"]

# Django container
FROM ghcr.io/trojsten/django-docker:v6 AS base

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY --chown=appuser:appuser ./ /app
COPY --chown=appuser:appuser --from=frontend-build /app/school/static/app.css /app/school/static/bundle.css /app/school/static/bundle.js /app/school/static/

RUN /app/docker/build.sh
ENV BASE_START=/app/docker/start.sh
