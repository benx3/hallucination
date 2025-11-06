@echo off
REM 🚀 Quick Deploy Script for Windows

echo 🧠 Hallucination Detection Dashboard - Quick Deploy
echo ==================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

echo ✅ Docker found

REM Check for .env file
if not exist ".env" (
    echo ⚠️  No .env file found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file with your API keys and press any key...
    pause
)

REM Check for config.json
if not exist "configs\config.json" (
    echo ⚠️  No config.json found. Creating from template...
    copy configs\config.example.json configs\config.json
    echo 📝 Please edit configs\config.json with your API keys and press any key...
    pause
)

echo 🔨 Building Docker image...
docker-compose build

if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo 🚀 Starting services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

echo ✅ Services started successfully!
echo.
echo 🌐 Dashboard URLs:
echo    Local: http://localhost:8502
echo    Nginx: http://localhost:80
echo.
echo 📊 Service Status:
docker-compose ps
echo.
echo 📝 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down
echo.
pause