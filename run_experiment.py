"""
Complete experiment runner using new unified architecture
"""
import os
import sys
sys.path.append('src')
sys.path.append('configs')

from src.api_runner import APIRunner
from src.evaluator import HallucinationEvaluator

def run_complete_experiment():
    """Run experiments across all APIs and datasets"""
    
    # Configuration
    apis = [
        {"provider": "openai", "model": "gpt-3.5-turbo", "api_key": os.getenv("OPENAI_API_KEY")},
        {"provider": "deepseek", "model": "deepseek-chat", "api_key": os.getenv("DEEPSEEK_API_KEY")},
        {"provider": "gemini", "model": "gemini-pro", "api_key": os.getenv("GOOGLE_API_KEY")},
        {"provider": "ollama", "model": "llama3.2", "base_url": "http://localhost:11434"}
    ]
    
    datasets = [
        "data/TruthfulQA.csv",
        "data/scientific_facts_basic.csv"
    ]
    
    evaluator = HallucinationEvaluator()
    
    for api_config in apis:
        provider = api_config["provider"]
        
        # Skip if no API key (except Ollama)
        if provider != "ollama" and not api_config.get("api_key"):
            print(f"Skipping {provider} - no API key")
            continue
            
        for dataset in datasets:
            if not os.path.exists(dataset):
                print(f"Skipping {dataset} - file not found")
                continue
                
            print(f"\n=== Running {provider} on {dataset} ===")
            
            # Setup paths
            dataset_name = os.path.basename(dataset).replace('.csv', '')
            output_dir = f"data/results/{provider}/{dataset_name}"
            results_csv = f"{output_dir}/results_raw.csv"
            
            try:
                # Run API experiment
                runner = APIRunner(
                    provider=provider,
                    model=api_config["model"],
                    api_key=api_config.get("api_key"),
                    base_url=api_config.get("base_url")
                )
                
                prompts = {
                    "direct": "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn. Nếu không chắc chắn, hãy nói 'không chắc'.\nCâu hỏi: {q}",
                    "selfcrit": "Nhiệm vụ: Trả lời rồi tự kiểm tra tính chính xác và sửa lại nếu cần.\nBước 1 — Nháp: trả lời ngắn.\nBước 2 — Tự kiểm: liệt kê điểm có thể sai hoặc thiếu.\nBước 3 — Cuối cùng: đưa đáp án cuối cùng. Nếu không chắc, hãy nói rõ không chắc.\nCâu hỏi: {q}"
                }
                
                runner.run_experiment(dataset, results_csv, prompts)
                
                # Run evaluation
                evaluator.run_evaluation(dataset, results_csv, output_dir)
                
                print(f"✓ Completed {provider} on {dataset_name}")
                
            except Exception as e:
                print(f"✗ Failed {provider} on {dataset_name}: {e}")

if __name__ == "__main__":
    run_complete_experiment()