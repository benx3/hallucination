#!/bin/bash

# 🚀 Quick Deploy Script for Hallucination Detection Dashboard

echo "🧠 Hallucination Detection Dashboard - Quick Deploy"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys:"
    echo "   nano .env"
    echo ""
    echo "Required keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - DEEPSEEK_API_KEY (optional)"
    echo "   - GOOGLE_API_KEY (optional)"
    echo ""
    read -p "Press Enter after editing .env file..."
fi

# Check if configs/config.json exists
if [ ! -f "configs/config.json" ]; then
    echo "⚠️  No config.json found. Creating from template..."
    cp configs/config.example.json configs/config.json
    echo "📝 Please edit configs/config.json with your API keys:"
    echo "   nano configs/config.json"
    echo ""
    read -p "Press Enter after editing config.json..."
fi

echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "🌐 Dashboard URLs:"
    echo "   Local: http://localhost:8502"
    if [ -f "nginx.conf" ]; then
        echo "   Nginx: http://localhost:80"
    fi
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📝 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop services:"
    echo "   docker-compose down"
else
    echo "❌ Services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi