# GeoQB SaaS - Local Development Makefile

.PHONY: help build up down restart logs logs-backend logs-frontend test clean reset

help: ## Show this help message
	@echo "GeoQB SaaS - Local Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "✅ Services starting..."
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

ps: ## Show service status
	docker-compose ps

test: ## Run backend tests
	docker-compose exec backend pytest -v

test-coverage: ## Run tests with coverage
	docker-compose exec backend pytest --cov=app --cov-report=html --cov-report=term

lint-backend: ## Lint backend code
	docker-compose exec backend black --check app/
	docker-compose exec backend ruff check app/

lint-frontend: ## Lint frontend code
	docker-compose exec frontend npm run lint

shell-backend: ## Access backend shell
	docker-compose exec backend /bin/sh

shell-frontend: ## Access frontend shell
	docker-compose exec frontend /bin/sh

db-shell: ## Access PostgreSQL shell
	docker-compose exec postgres psql -U geoqb -d geoqb

redis-cli: ## Access Redis CLI
	docker-compose exec redis redis-cli

db-reset: ## Reset database (WARNING: destroys all data)
	docker-compose down -v
	docker-compose up -d
	@echo "✅ Database reset complete"

clean: ## Remove all containers and images
	docker-compose down -v
	docker system prune -f

rebuild: down build up ## Full rebuild and restart

init: ## Initialize project (first time setup)
	@echo "🚀 Initializing GeoQB SaaS..."
	@if [ ! -f .env.local ]; then echo "✅ .env.local already exists"; fi
	docker-compose build
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ GeoQB SaaS is ready!"
	@echo ""
	@echo "   Frontend: http://localhost:3000"
	@echo "   Backend:  http://localhost:8000"
	@echo "   API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Run 'make help' for more commands"

status: ## Show detailed service status
	@echo "=== GeoQB SaaS Status ==="
	@docker-compose ps
	@echo ""
	@echo "=== Service Health ==="
	@curl -s http://localhost:8000/health 2>/dev/null && echo "✅ Backend: Healthy" || echo "❌ Backend: Unhealthy"
	@curl -s http://localhost:3000 > /dev/null 2>&1 && echo "✅ Frontend: Healthy" || echo "❌ Frontend: Unhealthy"

create-user: ## Create test user (email=test@example.com, password=testpass123)
	@echo "Creating test user..."
	@curl -X POST http://localhost:8000/api/v1/auth/signup \
		-H "Content-Type: application/json" \
		-d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}' \
		2>/dev/null | jq '.' || echo "Failed to create user"

backup-db: ## Backup database
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U geoqb geoqb > backups/backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "✅ Database backed up to backups/"

restore-db: ## Restore database from latest backup
	@latest=$$(ls -t backups/*.sql | head -1); \
	if [ -z "$$latest" ]; then \
		echo "❌ No backups found"; \
	else \
		echo "Restoring from $$latest..."; \
		docker-compose exec -T postgres psql -U geoqb -d geoqb < $$latest; \
		echo "✅ Database restored"; \
	fi
