# Comandos para Linux/Mac. No Windows, use os comandos equivalentes abaixo.

.PHONY: setup dev test lint check docker-up docker-down

setup:
	pip install -r requirements.txt
	cp .env.example .env

dev:
	uvicorn app.main:app --reload

test:
	pytest tests/ -v

lint:
	python -m py_compile app/**/*.py

check: lint test

docker-up:
	docker compose up -d

docker-down:
	docker compose down
