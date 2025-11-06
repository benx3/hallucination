# 🚀 Hướng dẫn Deploy lên Streamlit Cloud

## 📋 Tổng quan Streamlit Cloud

**Streamlit Cloud** (https://streamlit.io/cloud) là platform miễn phí của Streamlit để host các ứng dụng Streamlit trực tiếp từ GitHub repository.

### ✨ **Ưu điểm:**
- 🆓 **Miễn phí** - Không tốn phí hosting
- 🔄 **Auto-deploy** - Tự động deploy khi push code mới
- 🔒 **Secrets management** - Quản lý API keys an toàn
- 🌐 **Public URL** - Chia sẻ dễ dàng với bạn bè
- ⚡ **Fast setup** - Chỉ mất 5-10 phút

## 🔧 Bước 1: Chuẩn bị Repository

### 1.1 Kiểm tra files cần thiết
Repository của bạn đã có đầy đủ:
```
✅ ui/app.py              # Main Streamlit app
✅ requirements.txt       # Dependencies  
✅ README.md             # Documentation
✅ .gitignore            # Clean repository
```

### 1.2 Verify main app file
Streamlit Cloud sẽ chạy file `ui/app.py`, đảm bảo path này correct:
```
your-repo/
├── ui/
│   └── app.py  ← Main entry point
├── requirements.txt
└── ...
```

## 🌐 Bước 2: Truy cập Streamlit Cloud

### 2.1 Đăng nhập
1. Truy cập: **https://share.streamlit.io/**
2. Click **"Sign up"** hoặc **"Sign in"**
3. Chọn **"Continue with GitHub"**
4. Authorize Streamlit để access GitHub repositories

### 2.2 Kết nối GitHub
- Streamlit sẽ yêu cầu permission để access repositories
- Grant access để có thể deploy từ GitHub repo

## 🚀 Bước 3: Tạo App mới

### 3.1 Create new app
1. Click **"New app"** button
2. Chọn deployment method: **"From existing repo"**

### 3.2 Configure repository
**Repository settings:**
```
Repository: benx3/hallucination
Branch: main  
Main file path: ui/app.py
App URL (optional): hallucination-detection-dashboard
```

### 3.3 Advanced settings (Optional)
```
Python version: 3.9 (recommended)
```

## 🔐 Bước 4: Setup Secrets (API Keys)

### 4.1 Navigate to Secrets
1. Sau khi tạo app, click vào **"Settings"** 
2. Scroll down tới **"Secrets"** section

### 4.2 Add secrets
Trong **Secrets** textbox, thêm API keys theo format TOML:

```toml
# Streamlit secrets format
[secrets]
OPENAI_API_KEY = "sk-your-openai-key-here"
DEEPSEEK_API_KEY = "sk-your-deepseek-key-here" 
GOOGLE_API_KEY = "your-google-gemini-key-here"

# Optional: Ollama settings (for local testing only)
OLLAMA_BASE_URL = "http://localhost:11434"
```

### 4.3 Access secrets trong code
Code của bạn đã sẵn sàng với `st.secrets`:
```python
# ui/app.py đã có sẵn
import streamlit as st

# Access secrets
openai_key = st.secrets.get("OPENAI_API_KEY", "")
deepseek_key = st.secrets.get("DEEPSEEK_API_KEY", "")
google_key = st.secrets.get("GOOGLE_API_KEY", "")
```

## 🎯 Bước 5: Deploy App

### 5.1 Click Deploy
1. Sau khi setup xong repository và secrets
2. Click **"Deploy!"** button
3. Streamlit sẽ bắt đầu build và deploy

### 5.2 Monitor deployment
- **Build logs** sẽ hiển thị real-time
- Quá trình thường mất **2-5 phút**
- Nếu có lỗi, logs sẽ show chi tiết

### 5.3 Deployment success
Khi thành công, bạn sẽ nhận được:
```
🎉 Your app is live at:
https://benx3-hallucination-ui-app-xyz123.streamlit.app/
```

## 🔄 Bước 6: Auto-deployment

### 6.1 Automatic updates
- Mỗi khi bạn push code mới lên GitHub
- Streamlit Cloud sẽ **tự động rebuild và deploy**
- Không cần manual intervention

### 6.2 Monitor deployments
- Trong Streamlit Cloud dashboard
- Có thể xem **deployment history**
- Rollback nếu cần thiết

## 🛠️ Troubleshooting

### 6.1 Common issues

**❌ Build failed - Module not found:**
```bash
# Fix: Check requirements.txt
# Ensure all dependencies are listed with correct versions
```

**❌ Import errors:**
```python
# Fix: Update ui/app.py với proper imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**❌ API keys not working:**
```toml
# Fix: Double-check secrets format
# Ensure no extra spaces or quotes
OPENAI_API_KEY = "sk-actual-key-without-extra-quotes"
```

### 6.2 Debug logs
- Check **deployment logs** trong Streamlit Cloud
- Logs sẽ show exact error messages
- Fix issues và push lại

## 📱 Bước 7: Sharing & Usage

### 7.1 Get public URL
Sau khi deploy thành công:
```
Your app URL: 
https://benx3-hallucination-ui-app-xyz123.streamlit.app/

Share this URL với bạn bè! 🎉
```

### 7.2 App features sẽ work:
- ✅ **Enhanced Dashboard** với visual indicators
- ✅ **Hallucination Cases Analysis** 
- ✅ **Step-by-step Self-Critique display**
- ✅ **Model Comparison & Ranking**
- ✅ **Interactive filtering**
- ✅ **Real-time analytics**

### 7.3 Demo mode
Nếu không có API keys, app vẫn có thể:
- Load existing results từ `data/results/`
- Show pre-computed analysis
- Display charts và metrics

## 🎛️ Advanced Settings

### 8.1 Custom domain (Optional)
- Upgrade to **Streamlit for Teams** for custom domains
- Free tier sử dụng subdomain của Streamlit

### 8.2 Resource limits
**Free tier limits:**
- 📊 **CPU**: Shared resources
- 💾 **Memory**: 1GB RAM
- 💾 **Storage**: 1GB disk space
- 🌐 **Bandwidth**: Reasonable usage

### 8.3 Performance tips
```python
# Cache expensive operations
@st.cache_data
def load_large_dataset():
    return pd.read_csv("large_file.csv")

# Cache model results
@st.cache_resource  
def load_model():
    return expensive_model_loading()
```

## 📋 Final Checklist

**Trước khi deploy, check:**
- ✅ Repository public trên GitHub
- ✅ `ui/app.py` có thể chạy locally
- ✅ `requirements.txt` complete
- ✅ No hardcoded API keys trong code
- ✅ API keys added vào Streamlit Secrets
- ✅ Git history clean (no sensitive data)

**Sau khi deploy:**
- ✅ Test all features trên production URL
- ✅ Verify API connections work
- ✅ Share URL với team/bạn bè
- ✅ Monitor usage và performance

## 🎉 Kết quả

Sau khi hoàn thành, bạn sẽ có:

**🌐 Public URL**: `https://your-app.streamlit.app`
- Accessible từ anywhere
- Professional-looking dashboard
- Real-time LLM comparison
- Interactive hallucination analysis

**🔄 Auto-updates**: Push code → Auto deploy
**🔒 Secure**: API keys protected in secrets
**📊 Full features**: Tất cả enhanced features work
**🆓 Free**: No hosting costs

**Perfect cho sharing research results với advisor, colleagues, và academic community! 🎯**

---

### 🚀 Ready to deploy? 

1. Go to https://share.streamlit.io/
2. Sign in with GitHub  
3. Click "New app"
4. Repository: `benx3/hallucination`
5. Main file: `ui/app.py`
6. Add API keys to Secrets
7. Deploy! 

**Your Hallucination Detection Dashboard sẽ live trong vài phút! 🎉**