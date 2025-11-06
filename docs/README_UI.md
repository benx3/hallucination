# 🧠 Hallucination Detection Research - UI Version

## 🎯 Tổng quan

Giao diện web tương tác cho nghiên cứu hallucination detection với khả năng:

- ✅ **Multi-API Support**: OpenAI, DeepSeek, Gemini Pro, Ollama
- ✅ **Multi-Dataset**: Chọn datasets từ folder `data/`
- ✅ **Real-time Tracking**: Progress bars và status updates
- ✅ **Interactive Charts**: Plotly visualizations
- ✅ **Export Reports**: CSV, JSON, Text formats
- ✅ **Smart Caching**: Không re-run experiments đã có

## 🚀 Quick Start

### 1. Khởi động Demo (không cần API keys)
```bash
# Xem demo với fake data
streamlit run demo_ui.py
```

### 2. Setup Environment cho Production
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Setup API keys
set OPENAI_API_KEY=your_openai_key
set DEEPSEEK_API_KEY=your_deepseek_key  
set GOOGLE_API_KEY=your_google_key

# Start Ollama (optional)
ollama serve
ollama run llama3.2
```

### 3. Launch UI
```bash
# Tự động (Windows)
.\launch_ui.bat

# Manual
streamlit run app.py
```

Truy cập: **http://localhost:8501**

## 📁 Folder Structure

```
hallucination-research/
├── 🎨 UI Files
│   ├── app.py                     # Main Streamlit application
│   ├── demo_ui.py                 # Demo với fake data
│   ├── ui_experiment_runner.py    # Backend experiment logic
│   └── components/
│       └── analytics.py           # Advanced analytics
│
├── 📊 Data & Results
│   └── data/
│       ├── TruthfulQA.csv          # Complete research dataset (817 questions)
│       ├── scientific_facts_basic.csv # Scientific facts (100 questions)
│       └── results/              # All experiment results
│           ├── openai/
│           ├── deepseek/
│           ├── gemini/
│           └── ollama/
│
├── 🔧 Scripts (Updated for UI)
│   ├── openai_run.py             # API inference scripts
│   ├── deepseek_run.py
│   ├── gemini_run.py
│   ├── run_ollama_eval.py
│   ├── grade_and_report.py       # Evaluation logic
│   └── cross_model_comparison.py # Analysis scripts
│
└── 🚀 Setup Files
    ├── requirements.txt           # Dependencies
    ├── launch_ui.bat             # Windows launcher
    ├── launch_ui.ps1             # PowerShell launcher
    └── UI_GUIDE.md               # Detailed guide
```

## 🎮 UI Features Overview

### 🔧 Sidebar Configuration
- **API Selection**: Multi-select với availability checking
- **Model Selection**: Dropdown per API  
- **Dataset Selection**: Multi-select từ `data/` folder
- **One-click Launch**: Start all experiments

### 📊 Main Dashboard

#### Tab 1: 📈 Metrics Overview
- **Interactive Charts**: Accuracy vs Hallucination rates
- **Summary Stats**: Overall performance metrics
- **Real-time Updates**: Charts update as experiments complete

#### Tab 2: 📋 Detailed Results  
- **Results Table**: Chi tiết mỗi experiment
- **Question Analysis**: Drill-down vào individual questions
- **Error Tracking**: Failed experiments với error messages

#### Tab 3: 📄 Export Reports
- **Cross-Model Report**: Comprehensive comparison
- **CSV Export**: Raw data cho further analysis
- **Timestamped Downloads**: Automatic filename generation

## 🔍 Advanced Analytics

### Real-time Features:
- ⏱️ **Progress Tracking**: Overall + individual experiment progress
- 🔄 **Auto-refresh**: UI updates without manual refresh
- 💾 **Smart Caching**: Load existing results automatically
- 🚨 **Error Handling**: Continue on failures, show detailed errors

### Charts & Visualizations:
- 📊 **Bar Charts**: Accuracy comparison across APIs
- 📈 **Line Charts**: Improvement trends
- 🎯 **Scatter Plots**: Accuracy vs Hallucination trade-offs
- 🕸️ **Radar Charts**: Multi-dimensional API performance

### Export Options:
- 📝 **Text Reports**: Human-readable summaries
- 📊 **CSV Data**: Machine-readable results
- 📋 **JSON Metrics**: Structured experiment metadata
- 🕐 **Timestamped**: Automatic versioning

## ⚙️ Configuration

### Environment Variables
```bash
# Required for respective APIs
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...  
GOOGLE_API_KEY=AIza...

# Optional model overrides
OPENAI_MODEL=gpt-4o-mini
DEEPSEEK_MODEL=deepseek-chat
GEMINI_MODEL=gemini-1.5-flash
MODEL_NAME=llama3.2              # Ollama

# Optional path overrides  
DATA_DIR=data
RESULTS_DIR=data/results
TIMEOUT_S=300                    # Per-experiment timeout
```

### Streamlit Config (.streamlit/config.toml)
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

## 🔧 Development & Customization

### Adding New APIs:
1. Update `API_CONFIGS` in `app.py`
2. Create `{api_name}_run.py` script
3. Update `ui_experiment_runner.py`

### Adding New Metrics:
1. Modify `grade_and_report.py`
2. Update chart functions in `components/analytics.py`
3. Update export functions

### Custom Themes:
1. Modify `.streamlit/config.toml`
2. Add custom CSS với `st.markdown` trong `app.py`

## 📋 Workflow Example

1. **Setup**: Set API keys, prepare datasets
2. **Configure**: Select APIs và datasets trong sidebar
3. **Launch**: Click "Start Experiments"
4. **Monitor**: Watch real-time progress và results
5. **Analyze**: Explore charts và detailed results
6. **Export**: Download reports cho paper/presentation

## 🐛 Troubleshooting

### Common Issues:

**"No datasets found"**
```bash
python prep_additional_datasets.py
```

**"API unavailable"**
```bash
# Check environment
echo $OPENAI_API_KEY

# Set in current session
set OPENAI_API_KEY=your_key
```

**"Ollama connection failed"**
```bash
ollama serve
curl http://localhost:11434/api/tags
```

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

### Debug Tips:
- Check console output trong terminal
- Inspect `data/results/` folder cho partial results
- Run individual scripts manually để isolate issues
- Use demo mode để test UI features

## 🎯 Research Workflow

### For Academic Papers:
1. **Hypothesis Formation**: Use UI để explore initial results
2. **Experiment Design**: Configure systematic API/dataset combinations  
3. **Data Collection**: Run comprehensive experiments
4. **Analysis**: Use interactive charts để identify patterns
5. **Reporting**: Export data cho statistical analysis
6. **Visualization**: Screenshots của charts cho papers

### Best Practices:
- Start với demo để familiarize
- Test small experiments trước large-scale runs
- Save intermediate results frequently
- Document experimental settings
- Version control configurations

## 🏆 Benefits over Command Line

- ✅ **User-Friendly**: No need to remember commands
- ✅ **Visual Feedback**: Real-time progress và charts
- ✅ **Error Resilience**: Continue on individual failures
- ✅ **Data Exploration**: Interactive analysis tools
- ✅ **Export Ready**: One-click report generation
- ✅ **Reproducible**: Automatic configuration tracking

---

## 🚀 Ready to Start?

```bash
# Demo first (no setup required)
streamlit run demo_ui.py

# Then real experiments
streamlit run app.py
```

**Happy Researching! 🧠📊**