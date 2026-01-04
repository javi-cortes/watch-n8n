help:
	@echo "help            prints this help"
	@echo "up              build and start containers, then follow logs"
	@echo "down            stop and remove containers"
	@echo "stop            stop containers"
	@echo "build           build containers"
	@echo "logs            follow logs"
	@echo "test            run pytest inside api"
	@echo "lint            run mypy"
	@echo "psql            open psql to postgres"
	@echo "shell           open a shell in api container"
	@echo "migrations      create alembic revision autogenerate"
	@echo "migrate         run alembic upgrade head"
	@echo "version         print app version"
	@echo "clean           remove pyc and pycache"

dkc:=docker compose

include .env
export

up:
	@$(dkc) up --build -d
	@$(dkc) logs -f

down:
	@$(dkc) down

stop:
	@$(dkc) stop

build:
	@$(dkc) build

logs:
	@$(dkc) logs -f

test:
	@$(dkc) run --rm api pytest -vx

lint:
	mypy .

psql:
	@$(dkc) exec db psql --username=$$POSTGRES_USER --dbname=$$POSTGRES_DB

shell:
	@$(dkc) exec api bash

migrations:
	@$(dkc) run --rm api alembic -c $$APP_PATH/alembic.ini revision --autogenerate -m "auto"

migrate:
	@$(dkc) run --rm api alembic -c $$APP_PATH/alembic.ini upgrade head

version:
	@cat watch_n8n/__init__.py

clean:
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: help up down stop build logs test lint psql shell migrations migrate version clean
