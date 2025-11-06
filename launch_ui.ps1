# 🧠 Enhanced Hallucination Detection Research UI Launcher
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " 🧠 Enhanced Hallucination Detection Research UI" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✨ New Enhanced Features:" -ForegroundColor Yellow
Write-Host "  🎯 Visual indicators for Direct vs Self-Critique" -ForegroundColor White
Write-Host "  📊 Step-by-step self-critique analysis" -ForegroundColor White  
Write-Host "  🏆 Comprehensive model ranking dashboard" -ForegroundColor White
Write-Host "  🔍 Interactive hallucination cases filtering" -ForegroundColor White
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
& ".venv\Scripts\Activate.ps1"

# Install requirements
Write-Host "📦 Installing/updating requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check config
if (-not (Test-Path "configs\config.json")) {
    Write-Host ""
    Write-Host "⚠️  Configuration needed:" -ForegroundColor Red
    Write-Host "   1. Copy configs\config.example.json to configs\config.json" -ForegroundColor Yellow
    Write-Host "   2. Fill in your API keys in configs\config.json" -ForegroundColor Yellow
    Write-Host ""
}

# Launch Enhanced Streamlit app
Write-Host ""
Write-Host "🚀 Launching Enhanced Dashboard at http://localhost:8502" -ForegroundColor Green
Write-Host ""
python -m streamlit run ui/app.py --server.port 8502
