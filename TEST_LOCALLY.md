# 🎉 Test GeoQB SaaS Locally - Complete Guide

Your SaaS platform is ready to test! Follow this guide to run everything locally in Docker.

## 🚀 Quick Start (5 Minutes)

### 1. Start Everything

```bash
cd /home/user/geoqb

# Option A: Using Make (easiest)
make init

# Option B: Using Docker Compose
docker-compose up -d
```

### 2. Wait for Services (30 seconds)

Watch the logs until all services are healthy:
```bash
make logs
# Or: docker-compose logs -f
```

You should see:
```
✅ geoqb-postgres - database system is ready to accept connections
✅ geoqb-redis - Ready to accept connections
✅ geoqb-api - Application startup complete
✅ geoqb-web - ready - started server on 0.0.0.0:3000
```

### 3. Access the Platform

Open your browser to:
- **🌐 Frontend**: http://localhost:3000
- **📡 Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

## 📋 Complete Testing Checklist

### ✅ Test 1: Sign Up New User (Web UI)

1. Go to http://localhost:3000
2. Click "Get Started" or "Sign Up"
3. Fill in the form:
   - Email: `demo@geoqb.local`
   - Password: `demo123456` (min 8 chars)
   - Full Name: `Demo User`
4. Click "Create Account"
5. ✅ You should be redirected to the dashboard

### ✅ Test 2: Sign Up New User (API)

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api-test@geoqb.local",
    "password": "testpass123",
    "full_name": "API Test User"
  }'
```

Expected response:
```json
{
  "id": "uuid-here",
  "email": "api-test@geoqb.local",
  "full_name": "API Test User",
  "plan": "free",
  "status": "active",
  "is_verified": false,
  "created_at": "2024-..."
}
```

### ✅ Test 3: Login and Get Token

```bash
# Login via API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api-test@geoqb.local",
    "password": "testpass123"
  }'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Save the token:**
```bash
export TOKEN="your-access-token-here"
```

### ✅ Test 4: Create Workspace (Web UI)

1. Login to http://localhost:3000/auth/login
2. Go to Dashboard → Workspaces
3. Click "New Workspace"
4. Fill in:
   - Name: `My First Workspace`
   - Description: `Testing spatial analysis`
5. Click "Create"
6. ✅ Workspace should appear in the list

### ✅ Test 5: Create Workspace (API)

```bash
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Test Workspace",
    "description": "Created via API"
  }'
```

**Save the workspace ID from response:**
```bash
export WORKSPACE_ID="workspace-uuid-here"
```

### ✅ Test 6: Create Spatial Layer (API)

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

Expected response:
```json
{
  "id": "layer-uuid",
  "workspace_id": "workspace-uuid",
  "name": "Berlin Hospitals",
  "layer_type": "amenity",
  "tags": {"amenity": "hospital"},
  "bbox": [52.4, 13.2, 52.6, 13.5],
  "resolution": 9,
  "status": "pending",
  "feature_count": 0
}
```

### ✅ Test 7: List All Layers

```bash
curl -X GET http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/layers \
  -H "Authorization: Bearer $TOKEN"
```

### ✅ Test 8: Check Database Persistence

```bash
# Stop all services
make down
# Or: docker-compose down

# Start again
make up
# Or: docker-compose up -d

# Login again - your user and data should still exist!
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api-test@geoqb.local",
    "password": "testpass123"
  }'
```

### ✅ Test 9: Run Automated Tests

```bash
# Run all backend tests
make test

# Or with coverage
make test-coverage

# View coverage report
open geoqb-api/htmlcov/index.html
```

Expected output:
```
======================== test session starts =========================
collected 20+ items

tests/test_auth.py ..................  [90%]
tests/test_workspaces.py .........     [95%]
tests/test_layers.py ..........        [100%]

========================= 20 passed in 2.5s ==========================
```

### ✅ Test 10: Check Quota Enforcement

Create 6 layers (free tier limit is 5):

```bash
# Create 5 layers (should succeed)
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/layers \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Test Layer $i\",
      \"layer_type\": \"amenity\",
      \"tags\": {\"amenity\": \"cafe\"},
      \"bbox\": [52.4, 13.2, 52.6, 13.5],
      \"resolution\": 9
    }"
done

# Try to create 6th layer (should fail with quota error)
curl -X POST http://localhost:8000/api/v1/workspaces/$WORKSPACE_ID/layers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Layer 6",
    "layer_type": "amenity",
    "tags": {"amenity": "cafe"},
    "bbox": [52.4, 13.2, 52.6, 13.5],
    "resolution": 9
  }'
```

Expected error:
```json
{
  "detail": "Layer limit reached (5/5). Upgrade your plan to create more layers."
}
```

## 🔍 Verify Service Health

### Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "app": "GeoQB API",
  "version": "1.0.0",
  "environment": "development"
}
```

### Check Database

```bash
# Access PostgreSQL
make db-shell
# Or: docker-compose exec postgres psql -U geoqb -d geoqb

# Inside psql:
\dt                          # List all tables
SELECT * FROM users;         # View users
SELECT * FROM workspaces;    # View workspaces
SELECT * FROM layers;        # View layers
\q                          # Exit
```

### Check Redis

```bash
# Access Redis CLI
make redis-cli
# Or: docker-compose exec redis redis-cli

# Inside redis-cli:
KEYS *                      # List all keys
INFO                        # Redis info
EXIT                        # Exit
```

## 📊 View Logs

### All Services

```bash
make logs
# Or: docker-compose logs -f
```

### Specific Services

```bash
make logs-backend           # Backend only
make logs-frontend          # Frontend only
docker-compose logs postgres   # Database
docker-compose logs redis      # Cache
```

## 🎯 Common Workflows

### Development Workflow

1. **Make code changes** in `geoqb-api/app/` or `geoqb-web/src/`
2. **Auto-reload happens** (no restart needed!)
3. **Test immediately** in browser or via API
4. **View logs** with `make logs`

### Create Multiple Users

```bash
# Using Make (creates test@example.com)
make create-user

# Create custom user
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@test.com",
    "password": "password123",
    "full_name": "User One"
  }'

curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user2@test.com",
    "password": "password123",
    "full_name": "User Two"
  }'
```

### Test Complete User Journey

```bash
# 1. Signup
SIGNUP=$(curl -s -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"journey@test.com","password":"pass123","full_name":"Journey User"}')
echo "✅ Signed up: $SIGNUP"

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"journey@test.com","password":"pass123"}' | jq -r '.access_token')
echo "✅ Logged in, token: ${TOKEN:0:20}..."

# 3. Create Workspace
WS=$(curl -s -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Journey WS","description":"Complete test"}')
WS_ID=$(echo $WS | jq -r '.id')
echo "✅ Created workspace: $WS_ID"

# 4. Create Layer
LAYER=$(curl -s -X POST http://localhost:8000/api/v1/workspaces/$WS_ID/layers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Layer","layer_type":"amenity","tags":{"amenity":"hospital"},"bbox":[52.4,13.2,52.6,13.5],"resolution":9}')
LAYER_ID=$(echo $LAYER | jq -r '.id')
echo "✅ Created layer: $LAYER_ID"

# 5. List Layers
LAYERS=$(curl -s -X GET http://localhost:8000/api/v1/workspaces/$WS_ID/layers \
  -H "Authorization: Bearer $TOKEN")
echo "✅ Layers: $LAYERS"

echo ""
echo "🎉 Complete journey test successful!"
```

## 🛠️ Useful Make Commands

```bash
make help              # Show all commands
make status            # Service status
make ps                # Docker containers
make shell-backend     # Backend shell
make shell-frontend    # Frontend shell
make db-reset          # Reset database
make backup-db         # Backup database
make restore-db        # Restore database
make clean             # Remove everything
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check if ports are in use
lsof -i :3000   # Frontend
lsof -i :8000   # Backend
lsof -i :5432   # PostgreSQL
lsof -i :6379   # Redis

# Stop any conflicting processes or change ports in docker-compose.yml
```

### Backend Errors

```bash
# View backend logs
make logs-backend

# Check database connection
docker-compose exec backend python -c "from app.database import SessionLocal; SessionLocal()"

# Restart backend
docker-compose restart backend
```

### Frontend Errors

```bash
# View frontend logs
make logs-frontend

# Check environment variable
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Database Issues

```bash
# Check PostgreSQL status
docker-compose ps postgres

# Reset database (WARNING: deletes all data)
make db-reset

# Or manually:
docker-compose down -v
docker-compose up -d
```

### Port Conflicts

Edit `docker-compose.yml` and change ports:

```yaml
frontend:
  ports:
    - "3001:3000"  # Change 3000 to 3001

backend:
  ports:
    - "8001:8000"  # Change 8000 to 8001
```

## 📸 Screenshots

After testing, you should see:

### Frontend (http://localhost:3000)
- ✅ Beautiful landing page with animations
- ✅ Sign up / Login forms
- ✅ Dashboard with workspace list
- ✅ Workspace management UI
- ✅ Layer creation forms

### API Docs (http://localhost:8000/docs)
- ✅ Complete API documentation
- ✅ Interactive "Try it out" buttons
- ✅ Request/response examples
- ✅ Authentication section

## 🎉 Success Criteria

You've successfully tested the platform if:

- ✅ All services start without errors
- ✅ You can sign up and login via web UI
- ✅ You can sign up and login via API
- ✅ You can create workspaces
- ✅ You can create layers
- ✅ Data persists after restart
- ✅ Tests pass (make test)
- ✅ Quota limits are enforced
- ✅ API documentation is accessible
- ✅ Logs show no errors

## 🚀 Next Steps

Now that you've tested locally:

1. ✅ **Deploy to staging**: Follow `DEPLOYMENT_GUIDE.md`
2. ✅ **Set up monitoring**: Add Prometheus/Grafana
3. ✅ **Configure CI/CD**: GitHub Actions will deploy automatically
4. ✅ **Add payment integration**: Stripe setup
5. ✅ **Set up custom domain**: DNS configuration
6. ✅ **Enable SSL**: Let's Encrypt or managed certificates
7. 🚀 **Launch to production!**

## 💡 Pro Tips

1. **Keep services running**: Leave `make up` running during development
2. **Use separate terminals**: One for logs, one for commands
3. **Test API first**: Verify backend before testing UI
4. **Check logs often**: `make logs` shows issues immediately
5. **Backup before experiments**: `make backup-db`

## 📚 Documentation

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Local Development**: [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **SaaS Overview**: [SAAS_README.md](SAAS_README.md)
- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🆘 Need Help?

1. Check logs: `make logs`
2. Check status: `make status`
3. Try reset: `make db-reset`
4. Read troubleshooting: [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md#troubleshooting)
5. Check GitHub issues

---

**Happy Testing! 🎉**

Your production-ready SaaS platform is running locally and ready for development!
