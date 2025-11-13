@echo off
REM GeoQB SaaS - Easy Startup Script for Windows
REM This script starts the complete SaaS platform locally

echo.
echo    ____            ___  ____
echo   / ___^| ___  ___ / _ \^| __ )
echo  ^| ^|  _ / _ \/ _ \ ^| ^| ^|  _ \
echo  ^| ^|_^| ^|  __/ (_) ^| ^|_^| ^| ^|_) ^|
echo   \____^|\___^|\___/ \__\_\____/
echo.
echo   Spatial Knowledge Graph Platform
echo.

echo [32m Starting GeoQB SaaS Platform...[0m
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [33m Docker is not running![0m
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [34m Checking Docker Compose...[0m
docker-compose version >nul 2>&1
if errorlevel 1 (
    echo [33m Warning: docker-compose not found, using 'docker compose' instead[0m
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

REM Stop any existing services
echo [34m Stopping any existing services...[0m
%COMPOSE_CMD% down >nul 2>&1

REM Start services
echo [34m Building and starting services...[0m
echo    This may take a few minutes on first run...
%COMPOSE_CMD% up -d --build

REM Wait for services
echo [34m Waiting for services to be ready...[0m
timeout /t 5 /nobreak >nul

echo [34m Checking service health...[0m
echo.

REM Check services
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo   [33m Backend API (starting...)[0m
) else (
    echo   [32m Backend API[0m
)

curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    echo   [33m Frontend (starting...)[0m
) else (
    echo   [32m Frontend[0m
)

echo.
echo [32m GeoQB SaaS Platform is ready![0m
echo.

echo [34m Access your platform:[0m
echo    Frontend:     http://localhost:3000
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/docs
echo.

echo [34m Useful commands:[0m
echo    make logs              # View all logs
echo    make down              # Stop all services
echo    make test              # Run tests
echo.

echo [34m Next steps:[0m
echo    1. Open http://localhost:3000 in your browser
echo    2. Sign up for a new account
echo    3. Create your first workspace
echo    4. Add spatial layers and start analyzing!
echo.

echo [32m Happy building![0m
echo.

set /p LOGS="Would you like to view logs now? (y/N): "
if /i "%LOGS%"=="y" (
    %COMPOSE_CMD% logs -f
)
