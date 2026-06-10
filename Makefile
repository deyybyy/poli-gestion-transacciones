.PHONY: help build up down logs ps test lint fmt

help:
	@echo "Comandos disponibles:"
	@echo "  make build   - Construye las imágenes"
	@echo "  make up       - Levanta los contenedores en segundo plano"
	@echo "  make down     - Detiene y elimina los contenedores"
	@echo "  make logs     - Muestra los logs de la API"
	@echo "  make ps       - Lista el estado de los contenedores"
	@echo "  make test     - Ejecuta las pruebas"
	@echo "  make lint     - Verifica el estilo del código"
	@echo "  make fmt      - Formatea el código"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f api

ps:
	docker compose ps

test:
	pytest
