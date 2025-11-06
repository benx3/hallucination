# 🚀 HƯỚNG DẪN NHANH - Enhanced Hallucination Detection Dashboard

## ⚡ Chạy ngay với giao diện mới

### 1. Chuẩn bị môi trường
```bash
# Clone và cài đặt
git clone <repository-url>
cd halu2
pip install -r requirements.txt
```

### 2. Cấu hình API keys
```bash
# Copy file mẫu
copy configs\config.example.json configs\config.json

# Sửa configs\config.json - thêm API keys của bạn
```

### 3. Chạy giao diện nâng cao
```bash
# Cách 1: Double-click (Khuyến nghị)
launch_ui.bat

# Cách 2: Terminal
streamlit run ui\app.py --server.port 8502

# Cách 3: Menu tương tác
python main.py
```

### 4. Truy cập Dashboard
Mở trình duyệt: **http://localhost:8502**

## 🎯 Tính năng mới nổi bật

### 📊 Enhanced Hallucination Cases Analysis
- **Visual Indicators**: 🎯 Direct vs 🧠 Self-Critique badges
- **Step-by-Step Display**: Hiển thị từng bước trong quá trình Self-Critique
  - **Bước 1 - Nháp**: Câu trả lời ban đầu
  - **Bước 2 - Tự kiểm**: Quá trình tự kiểm tra
  - **Bước 3 - Cuối cùng**: Câu trả lời cuối cùng
- **Prompt Transparency**: Xem chính xác prompts được sử dụng
- **Interactive Filtering**: Lọc theo API, dataset, strategy

### 🏆 Model Ranking Dashboard
- **Real-time Comparison**: So sánh hiệu suất 4 LLMs
- **Composite Scoring**: Điểm tổng hợp từ nhiều metrics
- **Performance Breakdown**: Phân tích chi tiết từng khía cạnh

## 📋 Quy trình sử dụng nâng cao

### 1. Chuẩn bị và cấu hình
- **Tab "Configuration"** → Nhập API keys → Test kết nối ✅
- Kiểm tra các APIs: OpenAI, DeepSeek, Gemini, Ollama

### 2. Chạy thí nghiệm
- **Tab "Run Experiments"** → Chọn APIs + Datasets → Chạy 🚀
- Hỗ trợ chạy multiple APIs đồng thời
- Real-time progress tracking

### 3. Phân tích kết quả nâng cao
- **Tab "Results & Analytics"** → Xem metrics tổng quan 📊
- **Tab "Hallucination Cases Analysis"** → Phân tích chi tiết cases
- **Tab "Model Comparison"** → So sánh và ranking models 📈

### 4. Export và báo cáo
- Tải báo cáo Word với charts
- Export CSV data cho phân tích thêm
- Lưu metrics JSON cho tracking

## 📊 Datasets đã nâng cấp

- **astronomy_hard.csv** - 50 câu hỏi thiên văn khó
- **mathematics_hard.csv** - 50 câu hỏi toán học phức tạp  
- **questions_50_hard.csv** - 50 câu hỏi tổng hợp khó
- **scientific_facts_basic.csv** - 100 sự kiện khoa học cơ bản

## 🔧 Cấu hình API Keys

### File: configs/config.json
```json
{
  "openai": {
    "api_key": "sk-your-openai-key-here"
  },
  "deepseek": {
    "api_key": "sk-your-deepseek-key-here",
    "base_url": "https://api.deepseek.com"
  },
  "gemini": {
    "api_key": "your-google-gemini-key"
  },
  "ollama": {
    "base_url": "http://localhost:11434"
  }
}
```

## 🚀 Chạy thí nghiệm đầy đủ

### Option 1: UI Dashboard (Khuyến nghị)
```bash
launch_ui.bat
# → Truy cập http://localhost:8502
```

### Option 2: Script tự động
```bash
# Chạy tất cả APIs và datasets
python run_comprehensive_experiments.py

# Phân tích model comparison
python analyze_models.py
```

### Option 3: Menu tương tác  
```bash
python main.py
```

## 📈 Kết quả Model Ranking hiện tại

Dựa trên phân tích comprehensive từ tất cả datasets:

1. **🥇 Google Gemini Pro** (56.2/100)
   - Hiệu suất tổng thể tốt nhất
   - Uncertainty detection xuất sắc
   - Consistent across domains

2. **🥈 OpenAI GPT-4** (49.7/100)  
   - Độ ổn định cao
   - Cân bằng tốt các metrics
   - Hiệu suất đáng tin cậy

3. **🥉 DeepSeek** (49.6/100)
   - Tỷ lệ giá/hiệu suất tốt
   - Hiệu suất cạnh tranh
   - Lựa chọn cost-effective

4. **🏁 Ollama (Local)** (35.2/100)
   - Tập trung vào privacy
   - Không tốn phí API
   - Phù hợp cho dữ liệu nhạy cảm

## 🔍 Features nâng cao

### Enhanced Hallucination Analysis
- **716+ hallucination cases** được phân tích
- **Step-by-step reasoning** cho Self-Critique
- **Visual filtering** theo multiple criteria
- **Real-time metrics** dashboard

### Self-Critique Process Visualization
```
Bước 1 (Nháp) → Bước 2 (Tự kiểm) → Bước 3 (Cuối cùng)
     ↓              ↓                    ↓
   Draft         Self-Check           Final Answer
```

## 🛠️ Troubleshooting

### API Connection Issues
```bash
# Test individual APIs
python scripts/check_ollama.py  # For Ollama
# Check config.json format
# Verify API keys are valid
```

### UI không load
```bash
# Check port conflicts
netstat -an | findstr :8502

# Restart với port khác
streamlit run ui/app.py --server.port 8503
```

### Dependencies Issues
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## 📚 Tài liệu thêm

- [`UI_GUIDE.md`](UI_GUIDE.md) - Hướng dẫn sử dụng dashboard chi tiết
- [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md) - Cài đặt local models  
- [`README_COMPLETE_EXPERIMENT.md`](README_COMPLETE_EXPERIMENT.md) - Workflow đầy đủ

## 💡 Tips sử dụng hiệu quả

1. **Bắt đầu với 1 API** để test before scaling
2. **Sử dụng filtering** trong Hallucination Cases Analysis
3. **Compare models** ở tab Model Comparison  
4. **Export results** để phân tích offline
5. **Check step-by-step reasoning** để hiểu model behavior

Chúc bạn thành công với nghiên cứu hallucination detection! 🎯
    },
    "ollama": {
      "base_url": "http://localhost:11434"
    }
  }
}
```

## 📊 Datasets có sẵn

- **TruthfulQA.csv** - 817 câu hỏi nghiên cứu quốc tế về truthfulness
- **scientific_facts_basic.csv** - 100 sự kiện khoa học cơ bản (vật lý, hóa học, sinh học)

## ❓ Troubleshooting

### Lỗi import
```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### Lỗi API
- Kiểm tra API keys trong `config.json`
- Test connection trong UI

### Port đã dùng
```bash
streamlit run app.py --server.port 8502
```

## 🎯 Kết quả

Sau khi chạy xong:
- Metrics realtime trong UI
- Báo cáo Word tự động tạo
- CSV data trong `data/results/`
- Charts interactive với Plotly

---
📚 **Chi tiết**: Xem `README_UI.md` đầy đủ