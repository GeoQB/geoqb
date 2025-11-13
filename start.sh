#!/bin/bash

# GeoQB SaaS - Easy Startup Script
# This script starts the complete SaaS platform locally

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
   ____            ___  ____
  / ___| ___  ___ / _ \| __ )
 | |  _ / _ \/ _ \ | | |  _ \
 | |_| |  __/ (_) | |_| | |_) |
  \____|\___|\___/ \__\_\____/

  Spatial Knowledge Graph Platform
EOF
echo -e "${NC}"

echo -e "${GREEN}🚀 Starting GeoQB SaaS Platform...${NC}\n"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}❌ Docker is not running!${NC}"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo -e "${BLUE}📦 Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found, using 'docker compose' instead${NC}"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Stop any existing services
echo -e "${BLUE}🛑 Stopping any existing services...${NC}"
$COMPOSE_CMD down > /dev/null 2>&1 || true

# Start services
echo -e "${BLUE}🔧 Building and starting services...${NC}"
echo "   This may take a few minutes on first run..."
$COMPOSE_CMD up -d --build

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo -e "${BLUE}🔍 Checking service health...${NC}"

# Check PostgreSQL
if $COMPOSE_CMD exec -T postgres pg_isready -U geoqb > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ PostgreSQL${NC}"
else
    echo -e "  ${YELLOW}⏳ PostgreSQL (starting...)${NC}"
fi

# Check Redis
if $COMPOSE_CMD exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Redis${NC}"
else
    echo -e "  ${YELLOW}⏳ Redis (starting...)${NC}"
fi

# Check Backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Backend API${NC}"
else
    echo -e "  ${YELLOW}⏳ Backend API (starting...)${NC}"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Frontend${NC}"
else
    echo -e "  ${YELLOW}⏳ Frontend (starting...)${NC}"
fi

echo ""
echo -e "${GREEN}✨ GeoQB SaaS Platform is ready!${NC}\n"

echo -e "${BLUE}📍 Access your platform:${NC}"
echo -e "   ${GREEN}Frontend:${NC}     http://localhost:3000"
echo -e "   ${GREEN}Backend API:${NC}  http://localhost:8000"
echo -e "   ${GREEN}API Docs:${NC}     http://localhost:8000/docs"
echo ""

echo -e "${BLUE}📋 Useful commands:${NC}"
echo "   make logs              # View all logs"
echo "   make logs-backend      # View backend logs only"
echo "   make logs-frontend     # View frontend logs only"
echo "   make test              # Run tests"
echo "   make down              # Stop all services"
echo "   make db-reset          # Reset database"
echo ""

echo -e "${BLUE}🎯 Next steps:${NC}"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Sign up for a new account"
echo "   3. Create your first workspace"
echo "   4. Add spatial layers and start analyzing!"
echo ""

echo -e "${GREEN}Happy building! 🚀${NC}"

# Offer to show logs
read -p "Would you like to view logs now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $COMPOSE_CMD logs -f
fi
