#!/usr/bin/env python3
"""
Script to check and start Ollama server if needed
"""

import subprocess
import requests
import time
import sys
import os

def check_ollama_process():
    """Check if Ollama process is running"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq ollama.exe'], 
                                  capture_output=True, text=True)
            return 'ollama.exe' in result.stdout
        else:  # Linux/Mac
            result = subprocess.run(['pgrep', 'ollama'], 
                                  capture_output=True, text=True)
            return bool(result.stdout.strip())
    except Exception:
        return False

def check_ollama_api():
    """Check if Ollama API is responding"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def start_ollama():
    """Start Ollama server"""
    try:
        print("🚀 Starting Ollama server...")
        
        if os.name == 'nt':  # Windows
            # Try different ways to start Ollama on Windows
            try:
                subprocess.Popen(['ollama', 'serve'], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            except FileNotFoundError:
                # Try with full path if ollama not in PATH
                subprocess.Popen(['C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Ollama\\ollama.exe', 'serve'],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        print("⏳ Waiting for Ollama server to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_ollama_api():
                print("✅ Ollama server started successfully!")
                return True
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ Failed to start Ollama server within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def list_ollama_models():
    """List available Ollama models"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        return []
    except Exception:
        return []

def ensure_ollama_running():
    """Ensure Ollama is running, start if needed"""
    print("🔍 Checking Ollama status...")
    
    # Check if process is running
    if check_ollama_process():
        print("✅ Ollama process is running")
    else:
        print("❌ Ollama process not found")
        return start_ollama()
    
    # Check if API is responding
    if check_ollama_api():
        print("✅ Ollama API is responding")
        
        # List available models
        models = list_ollama_models()
        if models:
            print(f"📚 Available models: {', '.join(models)}")
        else:
            print("⚠️ No models found. You may need to pull a model:")
            print("   Example: ollama pull llama3.2")
        
        return True
    else:
        print("❌ Ollama API not responding")
        return start_ollama()

def main():
    """Main function"""
    print("🧠 Ollama Server Check & Start Tool")
    print("=" * 50)
    
    if ensure_ollama_running():
        print("\n🎉 Ollama is ready to use!")
        print("🌐 API endpoint: http://localhost:11434")
        
        # Test with a simple request
        try:
            response = requests.get('http://localhost:11434/api/tags')
            print("📊 API test successful")
        except Exception as e:
            print(f"⚠️ API test failed: {e}")
        
        return True
    else:
        print("\n❌ Failed to ensure Ollama is running")
        print("💡 Try manually starting Ollama:")
        if os.name == 'nt':
            print("   Windows: Run 'ollama serve' in Command Prompt")
        else:
            print("   Linux/Mac: Run 'ollama serve' in terminal")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)