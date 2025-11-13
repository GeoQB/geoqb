.PHONY: init up down logs clean restart rebuild

init:
	@echo "🚀 Initializing GeoQB SaaS..."
	docker-compose build
	docker-compose up -d
	@echo "✅ GeoQB is running!"
	@echo "   Backend API: http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"

up:
	@echo "▶️  Starting GeoQB services..."
	docker-compose up -d

down:
	@echo "⏹️  Stopping GeoQB services..."
	docker-compose down

logs:
	docker-compose logs -f

restart:
	@echo "🔄 Restarting GeoQB services..."
	docker-compose restart

rebuild:
	@echo "🔨 Rebuilding GeoQB services..."
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

clean:
	@echo "🧹 Cleaning up GeoQB..."
	docker-compose down -v
	docker system prune -f
