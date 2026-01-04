#!/usr/bin/env bash
set -e

APP_PATH="${APP_PATH:-/code}"

alembic -c "${APP_PATH}/alembic.ini" upgrade head

exec uvicorn watch_n8n.main:app --host 0.0.0.0 --port 8000 --reload
