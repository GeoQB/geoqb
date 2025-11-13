# 🚀 GeoQB SaaS - 5-Minute Quickstart

Get the complete SaaS platform running locally in 5 minutes!

## Prerequisites

- Docker Desktop installed and running
- 4GB RAM available for Docker

## Step 1: Clone and Navigate (30 seconds)

```bash
cd /path/to/geoqb
```

## Step 2: Start Everything (2 minutes)

```bash
# Option A: Using Make (recommended)
make init

# Option B: Using Docker Compose directly
docker-compose up -d
```

Wait for all services to start. You'll see:
```
✅ postgres  - healthy
✅ redis     - healthy
✅ backend   - started
✅ frontend  - started
```

## Step 3: Access the Application (30 seconds)

Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

## Step 4: Create Your First User (1 minute)

### Option A: Using the Web UI
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Fill in the form:
   - Email: test@example.com
   - Password: testpass123
   - Name: Test User
4. Click "Create Account"

### Option B: Using the API
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

### Option C: Using Make
```bash
make create-user
```

## Step 5: Test the Platform (1 minute)

1. **Login**: Go to http://localhost:3000/auth/login
2. **Create Workspace**: Click "New Workspace" in dashboard
3. **Create Layer**: Add a spatial layer with OSM data
4. **View API Docs**: Check http://localhost:8000/docs

## 🎉 You're Done!

You now have a complete SaaS platform running with:
- ✅ User authentication
- ✅ Workspace management
- ✅ Spatial layer creation
- ✅ PostgreSQL database
- ✅ Redis caching
- ✅ REST API with docs

## What's Running?

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Next.js web interface |
| Backend | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

## Quick Commands

```bash
# View logs
make logs                # All services
make logs-backend        # Backend only
make logs-frontend       # Frontend only

# Stop everything
make down

# Restart
make restart

# Run tests
make test

# Reset database (clears all data)
make db-reset

# Show status
make status
```

## Common Tasks

### Create a Workspace via API

```bash
# Login first
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  | jq -r '.access_token')

# Create workspace
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"My Workspace","description":"Test workspace"}'
```

### Create a Layer via API

```bash
# Get workspace ID from previous response or dashboard
WORKSPACE_ID="your-workspace-id"

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

## Troubleshooting

### Services won't start?

```bash
# Check if ports are available
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Check Docker is running
docker ps

# Reset everything
make db-reset
```

### Can't connect to API?

```bash
# Check backend health
curl http://localhost:8000/health

# View backend logs
make logs-backend
```

### Frontend shows connection error?

```bash
# Check environment variable
# Frontend needs: NEXT_PUBLIC_API_URL=http://localhost:8000

# Restart frontend
docker-compose restart frontend
```

## Next Steps

1. ✅ Explore the dashboard at http://localhost:3000/dashboard
2. ✅ Read API docs at http://localhost:8000/docs
3. ✅ Check [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for detailed guide
4. ✅ Run tests: `make test`
5. 🚀 Deploy to production: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## Development Workflow

### Make code changes:

**Backend**: Edit files in `geoqb-api/app/` → Auto-reload
**Frontend**: Edit files in `geoqb-web/src/` → Hot reload

### Run tests:

```bash
make test              # Backend tests
make test-coverage     # With coverage report
```

### View database:

```bash
make db-shell          # PostgreSQL CLI
make redis-cli         # Redis CLI
```

## Support

- **Documentation**: See `LOCAL_DEVELOPMENT.md`
- **API Docs**: http://localhost:8000/docs
- **Issue?**: Check logs with `make logs`

## Clean Up

```bash
# Stop services
make down

# Remove everything including data
make clean
```

---

**That's it! You have a production-ready SaaS platform running locally.** 🎉

Now go to http://localhost:3000 and start building!
