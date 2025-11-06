# 🧠 Hallucination Detection Research Project

A comprehensive research framework for comparing direct prompting vs self-critique prompting for hallucination detection in Vietnamese Q&A across multiple LLM APIs.

## 🚀 Quick Start

### Option 1: Interactive Menu
```bash
python main.py
```

### Option 2: Web UI
```bash
# Setup config first
copy configs/config.example.json configs/config.json
# Edit configs/config.json with your API keys

# Launch UI
python -m streamlit run ui/app.py
# OR double-click: launch_ui.bat
```

### Option 3: Direct Experiment
```bash
python run_experiment.py
```

## 📁 Project Structure

```
📦 halu2/
├── 📂 src/                    # Core source code
│   ├── api_runner.py          # Unified API runner (OpenAI, DeepSeek, Gemini, Ollama)
│   └── evaluator.py           # Evaluation and report generation
├── 📂 ui/                     # Web interface
│   ├── app.py                 # Main Streamlit application
│   ├── experiment_runner.py   # UI backend logic
│   └── components/            # UI components
├── 📂 configs/                # Configuration management
│   ├── config_manager.py      # API key management
│   ├── config.example.json    # Configuration template
│   └── config.json            # Your API keys (create from example)
├── 📂 scripts/                # Utility scripts
│   ├── prep_*.py             # Data preparation
│   ├── analyze_patterns.py   # Pattern analysis
│   └── cross_model_comparison.py
├── 📂 docs/                   # Documentation
│   ├── QUICK_START.md         # Quick start guide
│   ├── README_UI.md           # UI documentation
│   └── README_COMPLETE_EXPERIMENT.md
├── 📂 data/                   # Datasets and results
│   ├── TruthfulQA.csv             # TruthfulQA research dataset (817 questions)
│   ├── scientific_facts_basic.csv # Scientific facts dataset (100 questions)
│   └── results/               # Experiment outputs
├── 📄 main.py                 # Main entry point
├── 📄 run_experiment.py       # Complete experiment runner
└── 📄 launch_ui.bat          # Windows UI launcher
```

## 🎯 Features

### Multi-API Support
- ✅ **OpenAI** (GPT-3.5, GPT-4)
- ✅ **DeepSeek** (DeepSeek Chat, DeepSeek Coder)  
- ✅ **Google Gemini** (Gemini Pro, Gemini 1.5 Pro)
- ✅ **Ollama** (Local models: Llama, Qwen, etc.)

### Dual Prompting Strategy
- 🎯 **Direct Prompting**: Simple factual assistant
- 🔄 **Self-Critique Prompting**: 3-step process (draft → self-check → final answer)

### Comprehensive Evaluation
- 📊 **Correctness Detection**: Multi-format answer matching
- 🤔 **Uncertainty Detection**: Vietnamese/English uncertainty patterns
- 🚨 **Hallucination Detection**: Confident but incorrect responses
- 📈 **Cross-Model Comparison**: Performance across all APIs

### Rich Output Formats
- 📄 **Word Reports**: Academic-style experiment reports
- 📊 **JSON Metrics**: Structured performance data
- 🎨 **Interactive Charts**: Plotly visualizations
- 📋 **CSV Data**: Raw and processed results

## ⚙️ Configuration

### 1. API Keys Setup
```bash
# Copy template
cp configs/config.example.json configs/config.json

# Edit with your keys
{
  "apis": {
    "openai": {
      "api_key": "sk-your-openai-key",
      "models": ["gpt-3.5-turbo", "gpt-4"]
    },
    "deepseek": {
      "api_key": "sk-your-deepseek-key",
      "models": ["deepseek-chat"]
    },
    "gemini": {
      "api_key": "your-google-api-key",
      "models": ["gemini-pro"]
    },
    "ollama": {
      "base_url": "http://localhost:11434",
      "models": ["llama3.2", "qwen2.5"]
    }
  }
}
```

### 2. Environment Variables (Alternative)
```bash
export OPENAI_API_KEY="sk-..."
export DEEPSEEK_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
```

## 📊 Datasets

### Included Datasets
- **TruthfulQA.csv** - Complete TruthfulQA research dataset with 817 questions
- **scientific_facts_basic.csv** - Curated scientific facts covering physics, chemistry, biology
- **natural_questions_50.csv** - Natural Questions dataset  
- **fever_claims_50.csv** - FEVER fact-checking claims

### Custom Datasets
Add CSV files to `data/` with columns:
- `question` - The question text
- `answer` - Expected correct answer(s)
- `category` - Optional question category

## 🔬 Research Workflow

### 1. Experiment Execution
```
Dataset → API Runner → Raw Responses → Evaluator → Graded Results + Reports
```

### 2. Metrics Calculated
- **Correctness Rate**: % of accurate responses
- **Hallucination Rate**: % of confident but incorrect responses  
- **Uncertainty Rate**: % of responses expressing uncertainty
- **Response Time**: Average generation latency
- **Token Usage**: Input/output token consumption

### 3. Analysis Types
- **Direct vs Self-Critique**: Prompting strategy comparison
- **Cross-API Performance**: Model capability analysis
- **Question Difficulty**: Pattern-based difficulty scoring
- **Hallucination Patterns**: Error type categorization

## 🛠️ Development

### Requirements
```bash
pip install -r requirements.txt
```

### Key Dependencies
- `streamlit` - Web UI framework
- `openai` - OpenAI API client
- `google-generativeai` - Gemini API client
- `pandas` - Data processing
- `plotly` - Interactive visualizations
- `python-docx` - Word report generation

### Architecture
- **Unified API Runner**: Single interface for all LLM providers
- **Modular Evaluation**: Pluggable metrics and grading logic
- **Component-Based UI**: Reusable Streamlit components
- **Config-Driven**: JSON-based configuration management

## 📈 Results

### Output Structure
```
data/results/{api}/{dataset}/
├── results_raw.csv          # Raw API responses
├── results_graded.csv       # Evaluated responses
├── metrics.json             # Performance metrics
├── experiment_report.docx   # Word report
└── pattern_analysis.txt     # Hallucination patterns
```

### Metrics Interpretation
- **High Correctness** + **Low Hallucination** = Reliable model
- **High Uncertainty** = Calibrated confidence
- **Improvement Delta** = Self-critique effectiveness

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📝 Citation

```bibtex
@misc{hallucination_detection_2024,
  title={Hallucination Detection in Vietnamese Q&A: Direct vs Self-Critique Prompting},
  author={Your Name},
  year={2024},
  howpublished={GitHub Repository},
  url={https://github.com/your-repo/hallucination-detection}
}
```

## 📄 License

MIT License - see LICENSE file for details.

---

🔗 **Links**: [Quick Start](docs/QUICK_START.md) | [UI Guide](docs/README_UI.md) | [Technical Docs](.github/copilot-instructions.md)