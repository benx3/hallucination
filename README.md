# 🧠 Hallucination Detection Research Project

A comprehensive research framework for comparing **direct prompting** vs **self-critique prompting** for hallucination detection in Vietnamese Q&A across 4 LLM APIs: **OpenAI GPT-4**, **DeepSeek**, **Google Gemini Pro**, and **Ollama** (local models).

## ✨ Key Features

### 🎯 Enhanced UI Analytics
- **Visual Case Indicators**: 🎯 Direct prompting vs 🧠 Self-critique prompting badges
- **Step-by-Step Analysis**: Parse and display self-critique reasoning process (Bước 1→2→3)
- **Prompt Transparency**: View exact prompts used for each case
- **Interactive Filtering**: Filter hallucination cases by API, dataset, and prompt strategy

### 📊 Comprehensive Model Comparison
- **Automated Ranking System**: Composite scoring across multiple metrics
- **Performance Analysis**: Correctness, uncertainty detection, hallucination rates
- **Cross-Dataset Evaluation**: Performance consistency across different domains
- **Real-time Analytics**: Live dashboard with 716+ hallucination cases analyzed

### 🚀 Multi-API Architecture
- **Unified Interface**: Single codebase handles all 4 LLM providers
- **Consistent Output**: Standardized CSV schema across all APIs
- **Error Resilience**: Robust handling of API timeouts and rate limits
- **Environment Configuration**: Easy switching between models and datasets

## 🚀 Quick Start

### Option 1: Interactive Menu
```bash
python main.py
```

### Option 2: Enhanced Web Dashboard
```bash
# Setup configuration
copy configs/config.example.json configs/config.json
# Edit configs/config.json with your API keys

# Launch enhanced UI (recommended)
launch_ui.bat
# OR manually:
streamlit run ui/app.py --server.port 8502
```

### Option 3: Complete Experiments
```bash
# Run all APIs and datasets
python run_comprehensive_experiments.py

# Analyze model performance
python analyze_models.py
```

## 📁 Enhanced Project Structure

```
📦 halu2/
├── 📂 src/                          # Core logic
│   ├── api_runner.py                # Unified API interface with prompt saving
│   └── evaluator.py                 # Advanced grading and metrics
├── 📂 ui/                           # Enhanced Streamlit dashboard  
│   ├── app.py                       # Main UI with hallucination analysis
│   ├── experiment_runner.py         # Backend experiment management
│   └── components/
│       ├── analytics.py             # Basic analytics
│       └── enhanced_analytics.py    # Advanced hallucination visualization
├── 📂 data/                         # Datasets and organized results
│   ├── astronomy_hard.csv           # Astronomy questions
│   ├── mathematics_hard.csv         # Mathematics problems  
│   ├── questions_50_hard.csv        # General knowledge
│   ├── scientific_facts_basic.csv   # Science facts
│   └── results/                     # Results by API provider
│       ├── openai/                  # GPT-4 results
│       ├── deepseek/                # DeepSeek results  
│       ├── gemini/                  # Gemini Pro results
│       └── ollama/                  # Local model results
├── 📂 configs/                      # API configuration
│   ├── config_manager.py            # API key management
│   ├── config.example.json          # Configuration template
│   └── config.json                  # Your API keys
├── 📂 scripts/                      # Analysis utilities
│   ├── cross_model_comparison.py    # Cross-model analysis
│   ├── analyze_patterns.py          # Pattern detection
│   └── prep_additional_datasets.py  # Data preparation
├── 📂 docs/                         # Documentation
│   ├── QUICK_START.md               # Vietnamese quick start
│   ├── UI_GUIDE.md                  # Dashboard guide
│   └── OLLAMA_SETUP.md              # Local model setup
├── analyze_models.py                # Comprehensive model ranking
├── run_comprehensive_experiments.py # Full experiment pipeline
└── requirements.txt                 # Updated dependencies
```

## 🧠 Self-Critique Analysis

The project implements a sophisticated 3-step self-critique process:

1. **Bước 1 - Nháp**: Initial draft response
2. **Bước 2 - Tự kiểm**: Self-verification and critique  
3. **Bước 3 - Cuối cùng**: Final refined answer

The enhanced UI automatically parses these steps and displays them with structured formatting, making it easy to understand the model's reasoning process.

## 🏆 Current Model Rankings

Based on comprehensive analysis across all datasets:

1. **🥇 Google Gemini Pro** (56.2/100)
   - Best overall performance
   - Excellent uncertainty detection
   - Consistent across domains

2. **🥈 OpenAI GPT-4** (49.7/100)
   - Strong consistency
   - Good balance of metrics
   - Reliable performance

3. **🥉 DeepSeek** (49.6/100)
   - Good value proposition
   - Competitive performance
   - Cost-effective option

4. **🏁 Ollama (Local)** (35.2/100)
   - Privacy-focused option
   - No API costs
   - Suitable for sensitive data

## 📊 Advanced Features

### Hallucination Detection Logic
- **Correctness**: Vietnamese text normalization and containment checking
- **Uncertainty Detection**: Bilingual regex patterns for uncertainty expressions
- **Hallucination**: Confident but incorrect responses (NOT correct AND NOT uncertain)
- **Risk Scoring**: Question difficulty based on cross-model hallucination rates

### Enhanced UI Capabilities
- **Real-time Filtering**: Filter 716+ hallucination cases by multiple criteria
- **Visual Indicators**: Instant recognition of Direct vs Self-Critique cases
- **Step Parsing**: Automatic extraction and formatting of reasoning steps
- **Metrics Dashboard**: Live performance comparison across all APIs

### Data Flow Architecture
```
Input datasets → Multi-API runners → Raw results → Advanced grading → Enhanced analytics → Interactive dashboard
```

## 🔧 Configuration

### API Setup
Create `configs/config.json` from the example:
```json
{
  "openai": {
    "api_key": "your-openai-key"
  },
  "deepseek": {
    "api_key": "your-deepseek-key",
    "base_url": "https://api.deepseek.com"
  },
  "gemini": {
    "api_key": "your-gemini-key"
  },
  "ollama": {
    "base_url": "http://localhost:11434"
  }
}
```

### Environment Variables
```bash
MODEL_NAME=llama3.2              # For Ollama
API_PROVIDER=openai              # openai, deepseek, gemini, ollama  
INPUT_CSV=questions_50_hard.csv  # Input dataset
TIMEOUT_S=120                    # API timeout
```

## 🚀 Usage Examples

### Running Specific Analysis
```bash
# Single API experiment
python src/api_runner.py --api openai --dataset mathematics_hard.csv

# Model comparison with detailed breakdown
python analyze_models.py

# Launch enhanced dashboard
streamlit run ui/app.py --server.port 8502
```

### Analyzing Hallucination Cases
1. Launch the web dashboard: `launch_ui.bat`
2. Navigate to "Hallucination Cases Analysis" 
3. Filter by API, dataset, or prompt strategy
4. View step-by-step self-critique reasoning
5. Analyze visual indicators and patterns

## 📚 Documentation

- [`docs/QUICK_START.md`](docs/QUICK_START.md) - Vietnamese quick start guide
- [`docs/UI_GUIDE.md`](docs/UI_GUIDE.md) - Enhanced dashboard usage
- [`docs/OLLAMA_SETUP.md`](docs/OLLAMA_SETUP.md) - Local model configuration
- [`docs/README_COMPLETE_EXPERIMENT.md`](docs/README_COMPLETE_EXPERIMENT.md) - Full workflow

## 🛠️ Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd halu2
   pip install -r requirements.txt
   ```

2. **Configure APIs**
   ```bash
   copy configs/config.example.json configs/config.json
   # Edit config.json with your API keys
   ```

3. **Launch Dashboard**
   ```bash
   launch_ui.bat
   ```

## 🧪 Advanced Development

### Vietnamese Text Handling
- Bilingual prompt support (Vietnamese/English)
- Custom normalization for Vietnamese proper nouns
- Uncertainty pattern detection in both languages

### API Integration Patterns
- **OpenAI**: Official client with structured outputs
- **DeepSeek**: OpenAI-compatible client
- **Gemini**: Google AI client with safety settings
- **Ollama**: Direct HTTP requests to local server

### Output Formats
- **CSV**: Raw responses and graded results with prompt data
- **JSON**: Metrics and configuration files
- **Word**: Academic reports with charts and analysis
- **Interactive**: Real-time Streamlit dashboard

## 🤝 Contributing

1. Follow existing patterns in `src/api_runner.py`
2. Maintain consistent CSV output schema
3. Update evaluation logic and uncertainty patterns together
4. Test with multiple APIs before submitting changes

## 📄 License

This research project is for academic use. Please cite appropriately if used in publications.

---

For detailed usage instructions, see the Vietnamese guide: [`docs/QUICK_START.md`](docs/QUICK_START.md)