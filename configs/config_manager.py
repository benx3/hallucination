# config_manager.py - Quản lý API configuration và settings
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st

class ConfigManager:
    """Quản lý configuration cho API keys và settings"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        # Adjust example file path based on config file location
        config_dir = self.config_file.parent
        self.example_file = config_dir / "config.example.json"
        self.config = {}
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load configuration từ file hoặc tạo default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Tạo config.json từ example nếu chưa có
                self.create_default_config()
        except Exception as e:
            st.error(f"Lỗi khi load config: {e}")
            self.config = self.get_default_config()
    
    def create_default_config(self):
        """Tạo config.json từ example template"""
        if self.example_file.exists():
            try:
                # Copy example file thành config.json
                with open(self.example_file, 'r', encoding='utf-8') as f:
                    example_config = json.load(f)
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(example_config, f, indent=2, ensure_ascii=False)
                
                self.config = example_config
                st.info(f"✅ Đã tạo {self.config_file} từ template. Vui lòng điền API keys.")
            except Exception as e:
                st.error(f"Lỗi khi tạo config từ example: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Default configuration nếu không có file"""
        return {
            "apis": {
                "openai": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1",
                    "models": ["gpt-4o-mini", "gpt-4o"],
                    "default_model": "gpt-4o-mini"
                },
                "deepseek": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://api.deepseek.com",
                    "models": ["deepseek-chat"],
                    "default_model": "deepseek-chat"
                },
                "gemini": {
                    "enabled": False,
                    "api_key": "",
                    "base_url": "https://generativelanguage.googleapis.com",
                    "models": ["gemini-1.5-flash"],
                    "default_model": "gemini-1.5-flash"
                },
                "ollama": {
                    "enabled": True,
                    "api_key": None,
                    "base_url": "http://localhost:11434",
                    "models": ["llama3.2"],
                    "default_model": "llama3.2"
                }
            }
        }
    
    def save_config(self):
        """Lưu configuration vào file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Lỗi khi lưu config: {e}")
            return False
    
    def get_api_config(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Lấy config cho một API cụ thể"""
        return self.config.get("apis", {}).get(api_name.lower())
    
    def is_api_enabled(self, api_name: str) -> bool:
        """Kiểm tra API có được enable không"""
        api_config = self.get_api_config(api_name)
        if not api_config:
            return False
        
        # Kiểm tra enabled flag
        if not api_config.get("enabled", False):
            return False
        
        # Kiểm tra API key (trừ Ollama)
        if api_name.lower() != "ollama":
            api_key = api_config.get("api_key", "")
            if not api_key or api_key.startswith("YOUR_"):
                return False
        
        return True
    
    def get_available_apis(self) -> Dict[str, Dict[str, Any]]:
        """Lấy danh sách APIs available"""
        available = {}
        
        for api_name, api_config in self.config.get("apis", {}).items():
            if self.is_api_enabled(api_name):
                available[api_name] = api_config
        
        return available
    
    def get_api_models(self, api_name: str) -> list:
        """Lấy danh sách models cho API"""
        api_config = self.get_api_config(api_name)
        if api_config:
            return api_config.get("models", [])
        return []
    
    def get_default_model(self, api_name: str) -> str:
        """Lấy default model cho API"""
        api_config = self.get_api_config(api_name)
        if api_config:
            return api_config.get("default_model", "")
        return ""
    
    def update_api_key(self, api_name: str, api_key: str):
        """Cập nhật API key"""
        if "apis" not in self.config:
            self.config["apis"] = {}
        
        if api_name not in self.config["apis"]:
            self.config["apis"][api_name] = {}
        
        self.config["apis"][api_name]["api_key"] = api_key
        self.config["apis"][api_name]["enabled"] = bool(api_key)
    
    def test_api_connection(self, api_name: str) -> Dict[str, Any]:
        """Test kết nối tới API"""
        api_config = self.get_api_config(api_name)
        if not api_config:
            return {"success": False, "error": "API config not found"}
        
        try:
            if api_name.lower() == "ollama":
                # Test Ollama connection
                import requests
                response = requests.get(f"{api_config['base_url']}/api/tags", timeout=5)
                if response.status_code == 200:
                    return {"success": True, "message": "Ollama connection successful"}
                else:
                    return {"success": False, "error": f"Ollama server responded with {response.status_code}"}
                    
            elif api_name.lower() == "openai":
                # Test OpenAI API
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_config["api_key"],
                    base_url=api_config["base_url"]
                )
                
                # Simple test request
                response = client.chat.completions.create(
                    model=api_config["default_model"],
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return {"success": True, "message": "OpenAI API connection successful"}
                
            elif api_name.lower() == "deepseek":
                # Test DeepSeek API (OpenAI compatible)
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_config["api_key"],
                    base_url=api_config["base_url"]
                )
                
                response = client.chat.completions.create(
                    model=api_config["default_model"],
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                return {"success": True, "message": "DeepSeek API connection successful"}
                
            elif api_name.lower() == "gemini":
                # Test Gemini API
                import google.generativeai as genai
                genai.configure(api_key=api_config["api_key"])
                
                model = genai.GenerativeModel(api_config["default_model"])
                response = model.generate_content("Hello")
                
                return {"success": True, "message": "Gemini API connection successful"}
            
            else:
                return {"success": False, "error": f"Unknown API: {api_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Lấy UI configuration"""
        return self.config.get("ui", {
            "theme": "light",
            "port": 8501,
            "auto_refresh": True
        })
    
    def get_paths_config(self) -> Dict[str, str]:
        """Lấy paths configuration"""
        return self.config.get("paths", {
            "data_dir": "data",
            "results_dir": "data/results",
            "exports_dir": "exports"
        })
    
    def show_config_editor(self):
        """Hiển thị config editor trong Streamlit sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ API Configuration")
        
        # Kiểm tra config file exists
        if not self.config_file.exists():
            st.sidebar.error("❌ config.json not found")
            if st.sidebar.button("📁 Create Config File"):
                self.create_default_config()
                st.rerun()
            return
        
        # Show config status
        available_apis = self.get_available_apis()
        
        if available_apis:
            st.sidebar.success(f"✅ {len(available_apis)} APIs configured")
            
            # Show API status
            for api_name in ["openai", "deepseek", "gemini", "ollama"]:
                if api_name in available_apis:
                    st.sidebar.markdown(f"✅ {api_name.title()}")
                else:
                    st.sidebar.markdown(f"❌ {api_name.title()}")
        else:
            st.sidebar.error("❌ No APIs configured")
        
        # Quick config editor
        if st.sidebar.button("✏️ Edit Config"):
            st.session_state.show_config_editor = True
        
        # Full config editor (in modal or expander)
        if st.session_state.get("show_config_editor", False):
            self.show_full_config_editor()
    
    def show_full_config_editor(self):
        """Hiển thị full config editor"""
        st.markdown("### ⚙️ API Configuration Editor")
        
        apis_config = self.config.get("apis", {})
        updated = False
        
        for api_name, api_config in apis_config.items():
            st.markdown(f"#### {api_name.title()} API")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                enabled = st.checkbox(
                    "Enabled", 
                    value=api_config.get("enabled", False),
                    key=f"enabled_{api_name}"
                )
            
            with col2:
                if api_name != "ollama":
                    api_key = st.text_input(
                        "API Key",
                        value=api_config.get("api_key", ""),
                        type="password",
                        key=f"key_{api_name}",
                        help=f"Enter your {api_name.title()} API key"
                    )
                    
                    if api_key != api_config.get("api_key", ""):
                        self.update_api_key(api_name, api_key)
                        updated = True
                else:
                    st.info("Ollama runs locally - no API key needed")
            
            # Test connection button
            if st.button(f"🔍 Test {api_name.title()} Connection", key=f"test_{api_name}"):
                with st.spinner(f"Testing {api_name}..."):
                    result = self.test_api_connection(api_name)
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(f"Connection failed: {result['error']}")
            
            st.markdown("---")
        
        # Save button
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Config"):
                if self.save_config():
                    st.success("✅ Config saved!")
                    updated = True
                else:
                    st.error("❌ Save failed!")
        
        with col2:
            if st.button("🔄 Reload Config"):
                self.load_config()
                st.success("✅ Config reloaded!")
                st.rerun()
        
        with col3:
            if st.button("❌ Close Editor"):
                st.session_state.show_config_editor = False
                st.rerun()
        
        if updated:
            st.rerun()

def show_config_editor():
    """Hiển thị config editor trong Streamlit sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ API Configuration")
    
    config_manager = ConfigManager()
    
    # Kiểm tra config file exists
    if not config_manager.config_file.exists():
        st.sidebar.error("❌ config.json not found")
        if st.sidebar.button("📁 Create Config File"):
            config_manager.create_default_config()
            st.rerun()
        return config_manager
    
    # Show config status
    available_apis = config_manager.get_available_apis()
    
    if available_apis:
        st.sidebar.success(f"✅ {len(available_apis)} APIs configured")
        
        # Show API status
        for api_name in ["openai", "deepseek", "gemini", "ollama"]:
            if api_name in available_apis:
                st.sidebar.markdown(f"✅ {api_name.title()}")
            else:
                st.sidebar.markdown(f"❌ {api_name.title()}")
    else:
        st.sidebar.error("❌ No APIs configured")
    
    # Quick config editor
    if st.sidebar.button("✏️ Edit Config"):
        st.session_state.show_config_editor = True
    
    # Full config editor (in modal or expander)
    if st.session_state.get("show_config_editor", False):
        show_full_config_editor(config_manager)
    
    return config_manager

def show_full_config_editor(config_manager: ConfigManager):
    """Hiển thị full config editor"""
    st.markdown("### ⚙️ API Configuration Editor")
    
    apis_config = config_manager.config.get("apis", {})
    updated = False
    
    for api_name, api_config in apis_config.items():
        st.markdown(f"#### {api_name.title()} API")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            enabled = st.checkbox(
                "Enabled", 
                value=api_config.get("enabled", False),
                key=f"enabled_{api_name}"
            )
        
        with col2:
            if api_name != "ollama":
                api_key = st.text_input(
                    "API Key",
                    value=api_config.get("api_key", ""),
                    type="password",
                    key=f"key_{api_name}",
                    help=f"Enter your {api_name.title()} API key"
                )
                
                if api_key != api_config.get("api_key", ""):
                    config_manager.update_api_key(api_name, api_key)
                    updated = True
            else:
                st.info("Ollama runs locally - no API key needed")
        
        # Test connection button
        if st.button(f"🔍 Test {api_name.title()} Connection", key=f"test_{api_name}"):
            with st.spinner(f"Testing {api_name}..."):
                result = config_manager.test_api_connection(api_name)
                if result["success"]:
                    st.success(result["message"])
                else:
                    st.error(f"Connection failed: {result['error']}")
        
        st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Config"):
            if config_manager.save_config():
                st.success("✅ Config saved!")
                updated = True
            else:
                st.error("❌ Save failed!")
    
    with col2:
        if st.button("🔄 Reload Config"):
            config_manager.load_config()
            st.success("✅ Config reloaded!")
            st.rerun()
    
    with col3:
        if st.button("❌ Close Editor"):
            st.session_state.show_config_editor = False
            st.rerun()
    
    if updated:
        st.rerun()

# Global config manager instance
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    return config_manager