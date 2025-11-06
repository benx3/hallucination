# 🧠 Enhanced Hallucination Detection Dashboard - UI Guide

## 🎯 Tổng quan giao diện mới

Giao diện UI nâng cao cho phép bạn:
- ✅ **Multi-API Support**: OpenAI, DeepSeek, Gemini, Ollama với unified interface
- ✅ **Enhanced Analytics**: Phân tích hallucination cases với step-by-step reasoning
- ✅ **Visual Indicators**: Badges và icons phân biệt Direct vs Self-Critique
- ✅ **Real-time Dashboard**: Live metrics và interactive filtering
- ✅ **Model Comparison**: Comprehensive ranking với composite scoring
- ✅ **Prompt Transparency**: Xem exact prompts được sử dụng
- ✅ **Export Capabilities**: Báo cáo Word, CSV, JSON

## 🚀 Khởi động nhanh

### Bước 1: Setup môi trường nâng cao

```bash
# Cài đặt dependencies đã cập nhật
pip install -r requirements.txt

# Khởi động với port mới (recommended)
launch_ui.bat           # Tự động mở http://localhost:8502
```

### Bước 2: Setup API Keys (Cập nhật)

Tạo file `configs/config.json` từ template:
```json
{
  "openai": {
    "api_key": "sk-your-openai-key"
  },
  "deepseek": {
    "api_key": "sk-your-deepseek-key",
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

### Bước 3: Datasets có sẵn

Datasets đã được chuẩn bị trong `data/`:
- **astronomy_hard.csv** - 50 câu hỏi thiên văn khó
- **mathematics_hard.csv** - 50 câu hỏi toán học phức tạp
- **questions_50_hard.csv** - 50 câu hỏi tổng hợp khó
- **scientific_facts_basic.csv** - 100 sự kiện khoa học cơ bản
```

### Bước 4: Khởi động Enhanced UI

```bash
# Khởi động dashboard nâng cao
streamlit run ui/app.py --server.port 8502
```

Truy cập: **http://localhost:8502**

## 📋 Hướng dẫn sử dụng Enhanced Dashboard

### 🎯 Main Navigation Tabs

#### Tab 1: Configuration & Setup
- **API Status Check**: Xem trạng thái kết nối real-time
- **Model Selection**: Chọn models cho từng API
- **Dataset Preview**: Xem trước nội dung datasets

#### Tab 2: Run Experiments  
- **Multi-API Selection**: Chọn APIs muốn chạy đồng thời
- **Batch Processing**: Chạy tất cả combinations (API × Dataset)
- **Progress Tracking**: Real-time progress với detailed status

#### Tab 3: Results & Analytics
- **Overview Metrics**: Tổng quan performance tất cả models
- **Interactive Charts**: Plotly charts với drill-down capabilities
- **Performance Comparison**: Direct vs Self-Critique analysis

#### ⭐ Tab 4: Hallucination Cases Analysis (Mới!)
- **🎯 Visual Indicators**: Badges phân biệt Direct vs Self-Critique cases
- **🧠 Step-by-Step Display**: Parse và hiển thị từng bước reasoning
- **🔍 Interactive Filtering**: Filter theo API, dataset, strategy
- **📋 Prompt Transparency**: Xem exact prompts được sử dụng
- **📊 Case Statistics**: Metrics breakdown per category

#### ⭐ Tab 5: Model Comparison & Ranking (Mới!)
- **🏆 Comprehensive Ranking**: Top 4 LLMs với composite scores
- **📈 Performance Breakdown**: Chi tiết metrics từng model
- **📊 Cross-Dataset Analysis**: Consistency across domains
- **📋 Detailed Explanations**: Giải thích ranking rationale

### 🔍 Enhanced Analytics Features

#### 🧠 Self-Critique Process Visualization
```
Bước 1: Nháp          → Draft response
Bước 2: Tự kiểm       → Self-verification  
Bước 3: Cuối cùng     → Final refined answer
```

- **Automatic Step Parsing**: Regex extraction của Vietnamese step markers
- **Structured Display**: Organized presentation với markdown formatting
- **Content Analysis**: Show reasoning progression

#### 🎯 Visual Case Indicators
- **🎯 Direct Badge**: Simple prompting strategy
- **🧠 Self-Critique Badge**: Multi-step reasoning strategy  
- **Color Coding**: Green (correct), Red (hallucination), Yellow (uncertain)
- **Interactive Tooltips**: Hover for additional information

#### 📊 Advanced Filtering System
- **By API Provider**: OpenAI, DeepSeek, Gemini, Ollama
- **By Dataset**: Filter theo domain-specific datasets
- **By Strategy**: Direct vs Self-Critique
- **By Outcome**: Correct, Hallucination, Uncertain
- **Combined Filters**: Multiple criteria simultaneously

### 📁 Enhanced Project Structure

```
halu2/
├── ui/
│   ├── app.py                     # Enhanced main UI với new features
│   ├── experiment_runner.py       # Backend experiment management  
│   └── components/
│       ├── analytics.py           # Basic analytics components
│       └── enhanced_analytics.py  # Advanced hallucination analysis
├── data/
│   ├── astronomy_hard.csv         # 50 astronomy questions
│   ├── mathematics_hard.csv       # 50 math problems
│   ├── questions_50_hard.csv      # 50 general knowledge  
│   ├── scientific_facts_basic.csv # 100 scientific facts
│   └── results/                   # Organized by API provider
│       ├── openai/               # GPT-4 results with prompts
│       ├── deepseek/             # DeepSeek results with prompts
│       ├── gemini/               # Gemini Pro results with prompts
│       └── ollama/               # Local model results with prompts
├── analyze_models.py             # Comprehensive model comparison
├── run_comprehensive_experiments.py # Full pipeline automation
└── configs/
    ├── config.json               # API keys configuration  
    └── config.example.json       # Configuration template
```

## 🏆 Model Performance Dashboard

### Current Rankings (Real Data)
1. **🥇 Google Gemini Pro**: 56.2/100
   - Best uncertainty detection
   - Consistent performance across domains
   - Excellent self-critique improvement

2. **🥈 OpenAI GPT-4**: 49.7/100  
   - Strong baseline performance
   - Good balance across metrics
   - Reliable self-critique reasoning

3. **🥉 DeepSeek**: 49.6/100
   - Cost-effective performance
   - Competitive results
   - Good value proposition

4. **🏁 Ollama (Local)**: 35.2/100
   - Privacy-focused option
   - No API costs
   - Suitable for sensitive data

### Performance Metrics Explained
- **Composite Score**: Weighted average của correctness, uncertainty detection, hallucination rate
- **Self-Critique Improvement**: Tỷ lệ cải thiện khi sử dụng self-critique vs direct
- **Domain Consistency**: Performance stability across different datasets
- **Error Analysis**: Types of mistakes và patterns

## ⚙️ Advanced Configuration

### API Configuration (configs/config.json)
```json
{
  "openai": {
    "api_key": "sk-your-openai-key",
    "model": "gpt-4",
    "temperature": 0.1
  },
  "deepseek": {
    "api_key": "sk-your-deepseek-key", 
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
  },
  "gemini": {
    "api_key": "your-google-key",
    "model": "gemini-pro"
  },
  "ollama": {
    "base_url": "http://localhost:11434",
    "model": "llama3.2"
  }
}
```

### Environment Variables
```bash
# API Keys
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Model Selection (optional, có default)
OPENAI_MODEL=gpt-4o-mini
DEEPSEEK_MODEL=deepseek-chat
GEMINI_MODEL=gemini-1.5-flash
MODEL_NAME=llama3.2                # for Ollama

# Paths (optional, có default)
DATA_DIR=data
RESULTS_DIR=data/results

# Timeouts
TIMEOUT_S=300                       # Per experiment timeout
```

### Streamlit Configuration
Tạo `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## 🐛 Troubleshooting

### Common Issues:

1. **"No datasets found"**
   ```bash
   # Chạy để tạo datasets
   python prep_additional_datasets.py
   ```

2. **"API unavailable"**
   ```bash
   # Check environment variables
   echo $OPENAI_API_KEY
   
   # Hoặc set trong session
   export OPENAI_API_KEY=your_key
   ```

3. **"Ollama not available"**
   ```bash
   # Start Ollama server
   ollama serve
   
   # Check status
   curl http://localhost:11434/api/tags
   ```

4. **"Streamlit not found"**
   ```bash
   # Install dependencies
   pip install streamlit plotly pandas
   ```

5. **"Experiment timeout"**
   - Tăng `TIMEOUT_S` environment variable
   - Check internet connection cho cloud APIs
   - Check Ollama service cho local

### Debug Mode:
```bash
# Run với verbose logging
streamlit run app.py --logger.level=debug

# Check backend separately
python ui_experiment_runner.py
```

## 📈 Performance Tips

1. **Parallel Processing**: UI chạy experiments tuần tự để tránh rate limits
2. **Caching**: Existing results được load tự động
3. **Memory Management**: Large datasets được chunk processing
4. **Error Recovery**: Individual experiment failures không stop toàn bộ
5. **Progress Tracking**: Real-time updates không block UI

## 🎨 Customization

### Thêm API mới:
1. Update `API_CONFIGS` trong `app.py`
2. Tạo `{api_name}_run.py` script
3. Update `ui_experiment_runner.py`

### Thêm metrics mới:
1. Update `grade_and_report.py`
2. Update chart functions trong `components/analytics.py`
3. Update export functions

### Custom themes:
1. Modify `.streamlit/config.toml`
2. Update CSS trong `app.py` với `st.markdown`

## 🏆 Best Practices

1. **Start Small**: Test với 1-2 APIs và datasets trước
2. **Monitor Resources**: Check RAM/CPU usage với large experiments  
3. **Save Frequently**: UI tự động save, nhưng export quan trọng data
4. **Version Control**: Git track experiment configs và results
5. **Documentation**: Note experimental settings trong exported reports

---

**Happy Experimenting! 🚀**

Giao diện này giúp bạn dễ dàng so sánh hallucination detection across multiple LLMs và datasets, tạo ra insights valuable cho research paper của bạn!