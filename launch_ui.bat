@echo off
echo ====================================================
echo  🧠 Enhanced Hallucination Detection Research UI
echo ====================================================
echo.
echo ✨ New Features:
echo   🎯 Visual indicators for Direct vs Self-Critique
echo   📊 Step-by-step self-critique analysis  
echo   🏆 Comprehensive model ranking dashboard
echo   🔍 Interactive hallucination cases filtering
echo.
echo 📋 Setup Instructions:
echo   1. Copy configs/config.example.json to configs/config.json
echo   2. Fill in your API keys in configs/config.json
echo   3. Optional: Start Ollama locally (ollama serve)
echo.
echo 🌐 Dashboard will open at: http://localhost:8502
echo.
echo Press any key to launch the enhanced dashboard...
pause >nul
echo.
echo 🚀 Starting Enhanced Streamlit Dashboard...
E:\ThacSi\NLP\week5\halu2\.venv\Scripts\python.exe -m streamlit run ui/app.py --server.port 8502
