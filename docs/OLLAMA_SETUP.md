# Ollama Setup và Troubleshooting Guide

## 🔍 Kiểm tra Ollama đang chạy

### Method 1: PowerShell (Windows)
```powershell
# Check process
Get-Process ollama -ErrorAction SilentlyContinue

# Check API 
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get

# List models
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" | Select-Object -ExpandProperty models | Select-Object name
```

### Method 2: Command Line
```bash
# Check if server responds
curl http://localhost:11434/api/tags

# Or với Python
python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

## 🚀 Khởi động Ollama Server

### Windows:
```cmd
# Method 1: Command Prompt
ollama serve

# Method 2: Nếu không có trong PATH
C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe serve

# Method 3: PowerShell background
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
```

### Linux/Mac:
```bash
# Foreground
ollama serve

# Background  
nohup ollama serve > /dev/null 2>&1 &
```

## 📚 Quản lý Models

### Pull models (download):
```bash
# Llama 3.2 (2GB)
ollama pull llama3.2

# Llama 3.2 with vision
ollama pull llama3.2-vision

# Other popular models
ollama pull llama3.1:8b
ollama pull codellama
ollama pull mistral
```

### List available models:
```bash
ollama list
```

### Remove models:
```bash
ollama rm llama3.2
```

## 🔧 Troubleshooting

### Server không start:
1. **Check port 11434** có bị chiếm không:
   ```powershell
   netstat -ano | findstr 11434
   ```

2. **Kill existing process**:
   ```powershell
   Get-Process ollama | Stop-Process -Force
   ```

3. **Restart**:
   ```bash
   ollama serve
   ```

### API không respond:
1. **Firewall**: Đảm bảo port 11434 không bị block
2. **Antivirus**: Whitelist ollama.exe
3. **Restart**: Restart ollama service

### Model không tải được:
1. **Check internet connection**
2. **Check disk space** (models can be large)
3. **Try different model**:
   ```bash
   ollama pull llama3.2:1b  # Smaller version
   ```

## ⚙️ Configuration

### Custom host/port:
```bash
# Set environment variables
export OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

### Windows Environment Variables:
```cmd
set OLLAMA_HOST=0.0.0.0:11435
ollama serve
```

## 🧪 Test Connection

### Python test:
```python
import requests

try:
    response = requests.get('http://localhost:11434/api/tags')
    if response.status_code == 200:
        print("✅ Ollama is running")
        models = response.json()['models']
        print(f"📚 Available models: {len(models)}")
        for model in models:
            print(f"  - {model['name']}")
    else:
        print("❌ Ollama API error")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Quick API test:
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2", "prompt": "Hello", "stream": false}'
```

## 📖 Auto-start Script

Sử dụng script: `python scripts/check_ollama.py`

Script này sẽ:
- ✅ Check nếu Ollama đang chạy
- 🚀 Start server nếu chưa chạy  
- 📚 List available models
- 🧪 Test API connection

## 🔗 Useful Links

- **Ollama Official**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **API Docs**: https://github.com/ollama/ollama/blob/main/docs/api.md
- **Troubleshooting**: https://github.com/ollama/ollama/issues