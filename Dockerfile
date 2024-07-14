# Frontend builder
FROM node:20-alpine AS frontend-build

WORKDIR /app

COPY package.json package-lock.json /app/
RUN npm install

COPY school ./school
COPY css ./css
COPY tailwind.config.js ./tailwind.config.js
RUN npm run build && npm run build-js
CMD ["npm", "run", "dev"]

# Django container
FROM python:3.11-slim-bullseye AS base
WORKDIR /app
RUN useradd --create-home appuser \
    && chmod 777 /app \
    && chown appuser /app

ARG MULTIRUN_VERSION=1.1.3
ADD https://github.com/nicolas-van/multirun/releases/download/${MULTIRUN_VERSION}/multirun-x86_64-linux-gnu-${MULTIRUN_VERSION}.tar.gz /tmp
RUN tar -xf /tmp/multirun-x86_64-linux-gnu-${MULTIRUN_VERSION}.tar.gz \
    && mv multirun /bin \
    && rm /tmp/*

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY --chown=appuser:appuser . /app/
COPY --from=frontend-build /app/school/static/app.css /app/school/static/bundle.css /app/school/static/bundle.js /app/school/static/

CMD ["/bin/multirun", "caddy run --adapter caddyfile --config /app/Caddyfile", "/app/entrypoint.sh"]
