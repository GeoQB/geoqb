# GeoQB Quick Start Guide

Get up and running with GeoQB in under 5 minutes! ⚡

---

## Prerequisites

- **Docker Desktop** installed and running
- **Git** installed
- **Make** (optional, but recommended)

---

## 🚀 Option 1: Using Make (Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/GeoQB/geoqb.git
cd geoqb
```

### 2. Start Everything
```bash
make init
```

That's it! This single command will:
- ✅ Build all Docker images
- ✅ Start PostgreSQL, Redis, Backend API, and Frontend
- ✅ Initialize the database
- ✅ Run health checks

### 3. Access the Platform

Wait about 30 seconds for services to be ready, then open:

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/health

### 4. Create Your First Account

1. Go to http://localhost:3000
2. Click "Sign Up"
3. Enter your details (use any email for local dev)
4. Start creating layers!

---

## 🛠️ Option 2: Using Docker Compose Directly

If you don't have `make` installed:

```bash
# Clone the repo
git clone https://github.com/GeoQB/geoqb.git
cd geoqb

# Start all services
docker-compose up -d

# Watch logs (optional)
docker-compose logs -f
```

Access the platform at the same URLs as above.

---

## 📋 Useful Commands

### Service Management
```bash
# Start all services
make up

# Stop all services
make down

# View logs (follow mode)
make logs

# Restart everything
make restart

# Rebuild and restart
make rebuild

# Clean up everything (removes volumes)
make clean
```

### Individual Service Logs
```bash
# Backend API logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# Database logs
docker-compose logs -f postgres
```

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it geoqb-postgres psql -U geoqb -d geoqb

# Inside psql:
\dt          # List tables
\d users     # Describe users table
SELECT * FROM users;
```

### Redis Access
```bash
# Connect to Redis
docker exec -it geoqb-redis redis-cli

# Inside redis-cli:
KEYS *       # List all keys
GET key_name # Get value
```

---

## 🎯 Your First Layer

Once you're logged in, create your first spatial layer:

### Via Web UI (Easy)
1. Go to http://localhost:3000/dashboard
2. Click "New Layer"
3. Fill in:
   - **Name:** `my_first_layer`
   - **Location:** `Berlin, Germany`
   - **Tags:** `amenity:cafe`
4. Click "Create"
5. Watch as GeoQB fetches and processes the data!

### Via API (Advanced)
```bash
# 1. Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com", "password": "yourpassword"}'

# Save the access_token from response

# 2. Create a layer
curl -X POST http://localhost:8000/api/v1/layers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "berlin_restaurants",
    "location": "Berlin, Germany",
    "tags": {"amenity": "restaurant"},
    "radius": 5000,
    "h3_resolution": 9
  }'

# 3. List your layers
curl -X GET http://localhost:8000/api/v1/layers \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🧪 Running Tests

### Backend Tests
```bash
# Enter backend container
docker exec -it geoqb-api bash

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

### View Coverage Report
After running tests with coverage:
```bash
# From host machine
open geoqb-api/htmlcov/index.html  # macOS
xdg-open geoqb-api/htmlcov/index.html  # Linux
```

---

## 🔧 Troubleshooting

### Services Won't Start
```bash
# Check Docker is running
docker ps

# Check for port conflicts
lsof -i :8000   # Backend port
lsof -i :3000   # Frontend port
lsof -i :5432   # PostgreSQL port
lsof -i :6379   # Redis port

# If ports are in use, stop other services or change ports in docker-compose.yml
```

### Database Connection Errors
```bash
# Reset the database
docker-compose down -v
docker-compose up -d

# The database will be recreated automatically
```

### Frontend Build Errors
```bash
# Rebuild frontend
docker-compose build frontend --no-cache
docker-compose up -d frontend
```

### Backend Import Errors
```bash
# Rebuild backend
docker-compose build backend --no-cache
docker-compose up -d backend
```

### Clear Everything and Start Fresh
```bash
make clean
make init
```

---

## 📚 Next Steps

### Learn More
- **Full Documentation:** [SAAS_README.md](SAAS_README.md)
- **Market Research:** [MARKET_RESEARCH.md](MARKET_RESEARCH.md)
- **Implementation Strategy:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Marketing Plan:** [MARKETING_PLAN.md](MARKETING_PLAN.md)

### Try These Examples
1. **Create Multiple Layers** - Combine different amenity types
2. **Export Data** - Download your layers as GeoJSON
3. **API Integration** - Build a Jupyter notebook using the API
4. **Custom Scoring** - Implement your own sustainability metrics

### Development
- **Backend Code:** `geoqb-api/app/`
- **Frontend Code:** `geoqb-web/src/`
- **pyGeoQB Library:** `pyGeoQB/geoanalysis/`

Changes to code are hot-reloaded automatically!

### Join the Community
- **GitHub Issues:** Report bugs or request features
- **Discussions:** Share your use cases and ideas
- **Contributions:** PRs welcome!

---

## 🎓 Example Use Cases

### 1. Sustainability Analysis
Create layers for:
- Green spaces (`leisure:park`)
- Public transport (`public_transport:*`)
- Bike infrastructure (`highway:cycleway`)
- Renewable energy (`power:solar`)

Analyze walkability and environmental impact of neighborhoods.

### 2. Urban Planning
Compare different cities:
```bash
# Layer 1: Berlin cafes
# Layer 2: Paris cafes
# Layer 3: London cafes

# Analyze density and distribution patterns
```

### 3. Real Estate Analysis
Score properties based on proximity to:
- Schools (`amenity:school`)
- Hospitals (`amenity:hospital`)
- Shopping (`shop:*`)
- Entertainment (`amenity:cinema,theatre`)

### 4. Research Projects
Combine OpenStreetMap with:
- Census data
- Environmental sensors
- Social media geolocation
- Custom datasets via API

---

## 🐛 Common Issues

### "Port already in use"
**Problem:** Another service is using port 8000, 3000, 5432, or 6379

**Solution:** Either stop the conflicting service or edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001 (or any free port)
```

### "Database connection failed"
**Problem:** PostgreSQL container not ready yet

**Solution:** Wait 10 seconds and refresh. Check status:
```bash
docker-compose ps
docker-compose logs postgres
```

### "Module not found" errors
**Problem:** Python dependencies not installed

**Solution:** Rebuild the backend:
```bash
docker-compose build backend --no-cache
docker-compose restart backend
```

### Frontend shows "API connection error"
**Problem:** Backend not running or wrong API URL

**Solution:**
1. Check backend is running: http://localhost:8000/health
2. Check `NEXT_PUBLIC_API_URL` in docker-compose.yml
3. Check CORS settings in backend

---

## 📞 Getting Help

- **Documentation:** Check [SAAS_README.md](SAAS_README.md) for detailed info
- **API Docs:** http://localhost:8000/docs (interactive API documentation)
- **GitHub Issues:** https://github.com/GeoQB/geoqb/issues
- **Health Check:** http://localhost:8000/health

---

## ✅ Checklist

After following this guide, you should be able to:
- [ ] Access the frontend at http://localhost:3000
- [ ] Sign up and create an account
- [ ] Access API docs at http://localhost:8000/docs
- [ ] Create your first spatial layer
- [ ] View your layers in the dashboard
- [ ] Run tests successfully
- [ ] Make code changes and see them hot-reload

If you can check all boxes, you're ready to start building with GeoQB! 🎉

---

**Happy mapping! 🗺️**
