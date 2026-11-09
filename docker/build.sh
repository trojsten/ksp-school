#!/bin/bash
set -euo pipefail

UV_EXCLUDE_NEWER="7 days" uv run --no-cache pygmentize -S monokai -f html -a .codehilite > /app/school/static/code.css

export DATABASE_URL=sqlite://:memory:
export OIDC_RP_CLIENT_ID=not-provided
export OIDC_RP_CLIENT_SECRET=not-provided
export SCHOOL_IMPORT_TOKEN=not-provided

UV_EXCLUDE_NEWER="7 days" uv run --no-cache python manage.py collectstatic --no-input
