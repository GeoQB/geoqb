# Local Development Guide

Run the complete GeoQB SaaS platform locally using Docker Compose.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- At least 4GB RAM available for Docker
- Ports 3000, 8000, 5432, 6379 available

## Quick Start

### 1. Start All Services

```bash
# From the project root directory
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2. Wait for Services to be Ready

The first build will take a few minutes. Wait until you see:

```
✅ postgres     - healthy
✅ redis        - healthy
✅ backend      - Database initialized
✅ frontend     - ready on http://localhost:3000
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Create Your First User

Open http://localhost:3000 and click "Sign Up"

Or use the API directly:

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

## Service Architecture

```
┌─────────────────────────────────────────────────┐
│             Docker Compose Stack                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐        ┌──────────────┐     │
│  │   Frontend   │        │   Backend    │     │
│  │  (Next.js)   │───────▶│  (FastAPI)   │     │
│  │ Port: 3000   │        │  Port: 8000  │     │
│  └──────────────┘        └──────────────┘     │
│         │                        │             │
│         │                        │             │
│         │                ┌───────┴───────┐     │
│         │                │               │     │
│  ┌──────▼──────┐  ┌──────▼──────┐ ┌─────▼────┐│
│  │   Browser   │  │  PostgreSQL │ │  Redis   ││
│  │             │  │  Port: 5432 │ │ Port:6379││
│  └─────────────┘  └─────────────┘ └──────────┘│
│                                                 │
└─────────────────────────────────────────────────┘
```

## Common Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start with logs visible
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Rebuild After Code Changes

```bash
# Rebuild backend
docker-compose build backend
docker-compose up -d backend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Rebuild all
docker-compose build
docker-compose up -d
```

### Execute Commands in Containers

```bash
# Backend: Run database migrations
docker-compose exec backend python -c "from app.database import init_db; init_db()"

# Backend: Run tests
docker-compose exec backend pytest

# Backend: Access Python shell
docker-compose exec backend python

# PostgreSQL: Access database
docker-compose exec postgres psql -U geoqb -d geoqb

# Redis: Access CLI
docker-compose exec redis redis-cli
```

## Testing the Application

### 1. Sign Up Flow

```bash
# Sign up
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@geoqb.local",
    "password": "demo123456",
    "full_name": "Demo User"
  }'
```

### 2. Login and Get Token

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@geoqb.local",
    "password": "demo123456"
  }'

# Save the token
export TOKEN="your_access_token_here"
```

### 3. Create Workspace

```bash
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Workspace",
    "description": "Testing spatial analysis"
  }'

# Save the workspace ID
export WORKSPACE_ID="workspace_id_from_response"
```

### 4. Create Layer

```bash
curl -X POST http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/layers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Berlin Hospitals",
    "layer_type": "amenity",
    "tags": {"amenity": "hospital"},
    "bbox": [52.4, 13.2, 52.6, 13.5],
    "resolution": 9
  }'
```

### 5. List Layers

```bash
curl -X GET http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/layers \
  -H "Authorization: Bearer $TOKEN"
```

## Database Management

### View Database Contents

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U geoqb -d geoqb

# Inside psql:
\dt                          # List tables
SELECT * FROM users;         # View users
SELECT * FROM workspaces;    # View workspaces
SELECT * FROM layers;        # View layers
\q                          # Quit
```

### Reset Database

```bash
# Stop services and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Database will be recreated automatically
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U geoqb geoqb > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U geoqb -d geoqb < backup.sql
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :3000   # Frontend
lsof -i :8000   # Backend
lsof -i :5432   # PostgreSQL
lsof -i :6379   # Redis

# Kill the process or change ports in docker-compose.yml
```

### Services Not Starting

```bash
# Check service status
docker-compose ps

# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify database exists
docker-compose exec postgres psql -U geoqb -l

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Frontend Can't Reach Backend

```bash
# Check backend is healthy
curl http://localhost:8000/health

# Check CORS settings in docker-compose.yml
# Ensure CORS_ORIGINS includes http://localhost:3000

# Restart services
docker-compose restart
```

### "Module Not Found" Errors

```bash
# Rebuild with no cache
docker-compose build --no-cache backend
docker-compose up -d backend

# For frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Code Changes Not Reflected

For **backend** (Python):
```bash
# Check volume mounts in docker-compose.yml
# Ensure ./geoqb-api/app is mounted to /app/app

# Restart to reload
docker-compose restart backend
```

For **frontend** (Next.js):
```bash
# Hot reload should work automatically
# If not, restart:
docker-compose restart frontend
```

## Development Workflow

### Making Backend Changes

1. Edit files in `geoqb-api/app/`
2. Changes auto-reload (uvicorn --reload)
3. View logs: `docker-compose logs -f backend`
4. Test: `docker-compose exec backend pytest`

### Making Frontend Changes

1. Edit files in `geoqb-web/src/`
2. Hot reload happens automatically
3. View logs: `docker-compose logs -f frontend`
4. Build test: `docker-compose exec frontend npm run build`

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest -v

# Backend tests with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Frontend type check
docker-compose exec frontend npm run type-check

# Frontend lint
docker-compose exec frontend npm run lint
```

## Environment Variables

Edit `docker-compose.yml` to change environment variables:

```yaml
backend:
  environment:
    DEBUG: "True"                    # Enable debug mode
    FREE_PLAN_LAYER_LIMIT: "10"     # Increase free tier limit
    ACCESS_TOKEN_EXPIRE_MINUTES: "60"  # Longer tokens
```

## Accessing Services

### Backend API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Database Access

```bash
# Command line
docker-compose exec postgres psql -U geoqb -d geoqb

# Or use a GUI tool:
# Host: localhost
# Port: 5432
# Database: geoqb
# User: geoqb
# Password: geoqb_local_password
```

### Redis Access

```bash
# Redis CLI
docker-compose exec redis redis-cli

# Common commands:
KEYS *              # List all keys
GET key             # Get value
DEL key             # Delete key
FLUSHALL            # Clear all data
```

## Performance Tips

### Speed Up Builds

```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build
```

### Allocate More Memory

Increase Docker Desktop memory allocation:
- Mac: Docker Desktop → Preferences → Resources → Memory
- Windows: Docker Desktop → Settings → Resources → Memory

Recommended: 4GB minimum, 8GB optimal

### Clean Up Docker

```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Clean everything (careful!)
docker system prune -a
```

## Production Preview

To test production builds locally:

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Run production stack
docker-compose -f docker-compose.prod.yml up -d
```

## Next Steps

Once you've tested locally:

1. ✅ Test user signup/login flow
2. ✅ Create workspace and layers
3. ✅ Test API endpoints
4. ✅ Verify database persistence
5. ✅ Check logs for errors
6. ✅ Run test suite
7. 🚀 Deploy to production (see DEPLOYMENT_GUIDE.md)

## Support

Having issues?

1. Check logs: `docker-compose logs`
2. Check service status: `docker-compose ps`
3. Restart services: `docker-compose restart`
4. Reset everything: `docker-compose down -v && docker-compose up -d`
5. Check GitHub issues or create a new one

## Quick Reference

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Restart
docker-compose restart

# Rebuild
docker-compose build

# Reset
docker-compose down -v && docker-compose up -d

# Test
docker-compose exec backend pytest
```

Happy developing! 🚀
