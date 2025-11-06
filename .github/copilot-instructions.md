# Hallucination Detection Research Project

## Project Architecture

This is a comprehensive research project comparing **direct prompting** vs **self-critique prompting** for hallucination detection in Vietnamese Q&A across 4 LLM APIs: OpenAI, Ollama, DeepSeek, and Gemini Pro.

### Core Workflow
1. **Data preparation**: `prep_truthfulqa.py`, `prep_additional_datasets.py` convert datasets to CSV format
2. **Inference**: `openai_run.py`, `deepseek_run.py`, `gemini_run.py`, `run_ollama_eval.py` generate responses
3. **Evaluation**: `grade_and_report.py` scores responses and generates metrics + Word reports
4. **Pattern analysis**: `analyze_hallucination_patterns.py` identifies hallucination-prone question types
5. **Prompt optimization**: `test_improved_prompts.py` tests 7 improved prompt templates
6. **Cross-model comparison**: `cross_model_comparison.py` aggregates results across all models

### Directory Structure
- `ollama/`, `openai/`, `deepseek/`, `gemini/`: Results organized by API provider
- `improved_prompts/`: Testing of optimized prompt templates
- Each results directory contains: `results_raw.csv`, `results_graded.csv`, `metrics.json`, `pattern_analysis.txt`
- Input datasets: `TruthfulQA.csv`, `scientific_facts_basic.csv`

## Key Patterns

### Multi-API Architecture
All inference scripts follow identical patterns:
- **API abstraction**: `openai_run.py`, `deepseek_run.py` (OpenAI-compatible), `gemini_run.py` (Google AI), `run_ollama_eval.py` (local HTTP)
- **Dual prompting**: Direct vs self-critique strategies for each API
- **Error handling**: API timeouts, rate limiting, safety filters
- **Consistent output**: Same CSV schema across all providers

### Dual Prompting Strategy
- **Direct prompt**: Simple factual assistant role in Vietnamese 
- **Self-critique prompt**: 3-step process (draft → self-check → final answer)
- `extract_final()` function extracts final answer from self-critique responses using Vietnamese markers

### Advanced Evaluation Pipeline
- **Multi-dataset support**: TruthfulQA, Natural Questions, FEVER, custom science facts
- **Pattern analysis**: Automated detection of hallucination-prone question types (wh-questions, superlatives, technical terms)
- **Prompt optimization**: 7 improved templates (conservative, evidence-based, calibrated, meta-cognitive)
- **Cross-model comparison**: Aggregated metrics, difficulty scoring, model ranking

### Hallucination Detection Logic (`grade_and_report.py`)
- **Correctness**: String containment after normalization (handles multiple representations like "3e8" for speed of light)
- **Uncertainty detection**: Regex patterns for Vietnamese/English uncertainty expressions
- **Hallucination**: Incorrect AND not uncertain (confident but wrong answers)
- **Risk analysis**: Question-level difficulty scoring based on cross-model hallucination rates

### Environment Configuration
All scripts use consistent env var patterns:
```python
MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2") 
INPUT_CSV = os.getenv("INPUT_CSV", "questions_50.csv")
OUT_CSV = os.getenv("OUT_CSV", "results_raw.csv")
API_PROVIDER = os.getenv("API_PROVIDER", "openai")  # openai, deepseek, gemini
```

### Complete Experiment Workflow
```
Multiple datasets → prep_additional_datasets.py → questions_*.csv 
→ [openai_run.py|deepseek_run.py|gemini_run.py|run_ollama_eval.py] → results_raw.csv 
→ grade_and_report.py → results_graded.csv + metrics.json + pattern_analysis.txt
→ analyze_hallucination_patterns.py → improved_prompts.py
→ test_improved_prompts.py → prompt effectiveness analysis
→ cross_model_comparison.py → comprehensive comparison report
```

### Quick Start
Use `run_complete_experiment.py` to execute the full pipeline across all available APIs and datasets automatically.

## Development Notes

- **Vietnamese text handling**: All prompts and uncertainty patterns are bilingual (Vietnamese/English)
- **Normalization**: Custom text normalization for Vietnamese proper nouns and scientific terms
- **Output formats**: CSV for data processing, JSON for metrics, Word docs for academic reporting
- **API handling**: OpenAI uses official client; Ollama uses direct HTTP requests to localhost:11434; DeepSeek uses OpenAI-compatible client; Gemini uses google-generativeai
- **Timeouts**: Configurable via `TIMEOUT_S` environment variable (default 120s)
- **Rate limiting**: Built-in delays for Gemini API; configurable for others
- **Error resilience**: All scripts continue on individual failures, log errors appropriately

When modifying evaluation logic, update both the correctness checker and uncertainty patterns in `grade_and_report.py`. The normalization function handles domain-specific equivalencies crucial for accurate scoring. For adding new LLM providers, follow the pattern in existing `*_run.py` files with consistent CSV output schema.