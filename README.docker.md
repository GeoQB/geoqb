# GeoQB Docker Setup

This directory contains Docker configuration for running GeoQB as a SaaS application.

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your TigerGraph credentials and configuration

3. **Initialize and start services:**
   ```bash
   make init
   ```

This will:
- Build Docker images
- Start backend API (port 8000)
- Start frontend (port 3000)

## Services

### Backend API
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Interactive API documentation)
- **Health:** http://localhost:8000/health

### Frontend
- **URL:** http://localhost:3000
- (Placeholder - ready for React/Vue integration)

## Makefile Commands

```bash
make init      # Initialize and start all services
make up        # Start services
make down      # Stop services
make logs      # View logs (follow mode)
make restart   # Restart all services
make rebuild   # Rebuild images from scratch
make clean     # Stop services and clean up volumes
```

## API Endpoints

### Layer Management
- `GET /api/v1/layers` - List all layers
- `POST /api/v1/layers` - Create a new layer
- `GET /api/v1/layers/{name}` - Get layer details
- `DELETE /api/v1/layers/{name}` - Delete a layer

### Analytics
- `POST /api/v1/analytics/impact-score` - Calculate sustainability impact score
- `GET /api/v1/analytics/clusters/{layer_name}` - Get spatial clusters

### Workspace
- `GET /api/v1/workspace/status` - Get workspace status

## Directory Structure

```
geoqb/
├── docker/
│   ├── Dockerfile.backend      # Backend API Dockerfile
│   ├── Dockerfile.frontend     # Frontend Dockerfile
│   └── app/
│       ├── main.py            # FastAPI application
│       └── __init__.py
├── docker-compose.yml         # Docker Compose configuration
├── Makefile                   # Build and run commands
├── .env.example              # Example environment variables
├── .dockerignore             # Docker build ignore patterns
└── pyGeoQB/                  # GeoQB Python library (mounted as volume)
```

## Development

### Backend Development

The backend code is mounted as a volume, so changes to `docker/app/` will automatically reload (when `--reload` flag is active).

### Logs

View logs for all services:
```bash
make logs
```

Or for specific service:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Shell Access

Get a shell in the backend container:
```bash
docker-compose exec backend bash
```

### Integrating with pyGeoQB

The backend has access to the `pyGeoQB` library. To use it in your API endpoints:

```python
import sys
sys.path.insert(0, '/app')

from pyGeoQB.geoanalysis.geoqb.geoqb_layers import LayerSpecification
from pyGeoQB.geoanalysis.geoqb.geoqb_tg import GeoQBTigerGraph

# Use the library
layer = LayerSpecification(name="test", location="Berlin", radius=5000)
```

## Troubleshooting

### Build Context Error

If you see an error about files not found during build:
- Ensure you're running commands from the **root geoqb directory**
- The build context is set to `.` (root) in docker-compose.yml
- All COPY commands in Dockerfiles use paths relative to the root

### TigerGraph Connection

Ensure your `.env` file has correct TigerGraph credentials:
```bash
TG_HOST=https://your-instance.i.tgcloud.io
TG_USERNAME=tigergraph
TG_PASSWORD=your-password
TG_GRAPHNAME=GeoQB
```

### Port Already in Use

If port 8000 or 3000 is already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

## Production Deployment

For production:
1. Remove `--reload` flag from uvicorn command
2. Configure proper CORS origins in `docker/app/main.py`
3. Use environment-specific `.env` files
4. Set up proper secrets management
5. Add HTTPS/SSL termination
6. Configure health checks and monitoring

## Next Steps

- [ ] Integrate pyGeoQB layer management into API endpoints
- [ ] Add authentication/authorization
- [ ] Build React/Vue frontend
- [ ] Add database for user management
- [ ] Implement caching (Redis)
- [ ] Add job queue for long-running tasks (Celery)
- [ ] Set up monitoring and logging
