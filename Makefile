.PHONY: install run test lint format migrate upgrade seed docker-up docker-down

VENV ?= .venv
PY   ?= $(VENV)/bin/python

install:            ## Create venv and install dev dependencies
	python -m venv $(VENV)
	$(PY) -m pip install -r requirements-dev.txt

run:                ## Run the development server
	$(PY) -m flask --app wsgi run --debug

test:               ## Run the test suite
	$(PY) -m pytest

lint:               ## Lint with ruff
	$(PY) -m ruff check .

format:             ## Auto-format with ruff
	$(PY) -m ruff format .

migrate:            ## Generate a migration (make migrate m="add foo")
	$(PY) -m flask --app wsgi db migrate -m "$(m)"

upgrade:            ## Apply migrations
	$(PY) -m flask --app wsgi db upgrade

seed:               ## Seed the admin user
	$(PY) -m flask --app wsgi seed-admin

docker-up:          ## Start API + Postgres with Docker Compose
	docker compose up --build -d

docker-down:        ## Stop and remove containers
	docker compose down
