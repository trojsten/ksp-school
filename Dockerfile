# Frontend builder
FROM node:current AS frontend-build
WORKDIR /app
RUN npm install -g pnpm@~6.24.3
COPY package.json pnpm-lock.yaml /app/
RUN pnpm install

COPY . /app/
RUN pnpm run build
CMD ["pnpm", "run", "dev"]

# Django container
FROM python:3.10 AS base
WORKDIR /app
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip install --upgrade "pipenv==2021.11.23"
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy

COPY . /app/
CMD ["/app/entrypoint.sh"]
