@echo off
echo ======================================
echo NoteAI Backend - Quick Start Script
echo ======================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo X Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo √ Docker is running
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠ .env file not found. Copying from .env.example...
    copy .env.example .env
    echo √ .env file created
    echo.
    echo ⚠ IMPORTANT: Please edit .env file and add your Naver Cloud API keys!
    echo    Required keys:
    echo    - NAVER_API_KEY
    echo    - NAVER_API_SECRET
    echo    - NAVER_APIGW_KEY
    echo    - HYPERCLOVA_API_KEY
    echo    - CLOVA_EMBEDDING_API_KEY
    echo.
    pause
)

echo Starting NoteAI Backend...
echo.

REM Build and start services
docker-compose up --build -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo Service Status:
echo ======================================
docker-compose ps

echo.
echo √ NoteAI Backend is running!
echo.
echo Available services:
echo   - API:              http://localhost:8000
echo   - API Docs:         http://localhost:8000/docs
echo   - Health Check:     http://localhost:8000/health
echo   - Celery Monitor:   http://localhost:5555
echo.
echo To view logs:
echo   docker-compose logs -f app
echo.
echo To stop services:
echo   docker-compose down
echo.
echo To run tests:
echo   python test_api.py
echo.
pause
