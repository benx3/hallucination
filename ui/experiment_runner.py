# ui_experiment_runner.py - Backend runner for UI experiments
# Separate backend logic to avoid UI blocking

import os
import subprocess
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
import time

class ExperimentRunner:
    """Backend class to run experiments for the UI"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.results_dir = self.data_dir / "results" 
        self.datasets_dir = self.data_dir
        
        # Ensure directories exist
        self.results_dir.mkdir(exist_ok=True)
        for api in ["openai", "deepseek", "gemini", "ollama"]:
            (self.results_dir / api).mkdir(exist_ok=True)
    
    def get_available_datasets(self) -> list:
        """Get list of available datasets"""
        datasets = []
        for file in self.datasets_dir.glob("*.csv"):
            if file.stem not in ['train']:  # Exclude non-QA files
                datasets.append(file.name)
        return sorted(datasets)
    
    def check_api_availability(self) -> Dict[str, bool]:
        """Check which APIs are available"""
        available = {}
        
        # Check API keys
        api_keys = {
            "OpenAI": "OPENAI_API_KEY",
            "DeepSeek": "DEEPSEEK_API_KEY", 
            "Gemini": "GOOGLE_API_KEY"
        }
        
        for api, env_key in api_keys.items():
            available[api] = bool(os.getenv(env_key))
        
        # Check Ollama
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/tags", timeout=3)
            available["Ollama"] = resp.status_code == 200
        except:
            available["Ollama"] = False
        
        return available
    
    def run_single_experiment(self, api_name: str, model_name: str, 
                            dataset_name: str) -> Dict:
        """Run a single experiment"""
        try:
            # Setup paths
            dataset_path = self.datasets_dir / dataset_name
            result_dir = self.results_dir / api_name.lower()
            
            dataset_base = dataset_name.replace('.csv', '')
            raw_output = result_dir / f"results_raw_{dataset_base}.csv"
            graded_output = result_dir / f"results_graded_{dataset_base}.csv"
            metrics_output = result_dir / f"metrics_{dataset_base}.json"
            
            # API script mapping
            script_mapping = {
                "OpenAI": "openai_run.py",
                "DeepSeek": "deepseek_run.py",
                "Gemini": "gemini_run.py", 
                "Ollama": "run_ollama_eval.py"
            }
            
            # Step 1: Run inference
            script = script_mapping[api_name]
            cmd = f'python {script}'
            
            env = os.environ.copy()
            env["INPUT_CSV"] = str(dataset_path)
            env["OUT_CSV"] = str(raw_output)
            
            # Set model-specific environment variables
            if api_name == "OpenAI":
                env["OPENAI_MODEL"] = model_name
            elif api_name == "DeepSeek":
                env["DEEPSEEK_MODEL"] = model_name
            elif api_name == "Gemini":
                env["GEMINI_MODEL"] = model_name
            elif api_name == "Ollama":
                env["MODEL_NAME"] = model_name
            
            # Run inference with timeout
            result = subprocess.run(
                cmd, shell=True, env=env, 
                capture_output=True, text=True, timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Inference failed: {result.stderr}"
                }
            
            # Step 2: Grade results
            cmd = "python grade_and_report.py"
            env["INPUT_QA"] = str(dataset_path)
            env["INPUT_RAW"] = str(raw_output)
            env["OUT_GRADED"] = str(graded_output)
            env["OUT_JSON"] = str(metrics_output)
            
            result = subprocess.run(
                cmd, shell=True, env=env,
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Grading failed: {result.stderr}"
                }
            
            # Load results
            metrics = {}
            if metrics_output.exists():
                with open(metrics_output, 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
            
            graded_df = pd.DataFrame()
            if graded_output.exists():
                graded_df = pd.read_csv(graded_output)
            
            return {
                "success": True,
                "metrics": metrics,
                "graded_data": graded_df,
                "files": {
                    "raw": str(raw_output),
                    "graded": str(graded_output),
                    "metrics": str(metrics_output)
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Experiment timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def load_existing_results(self) -> Dict[Tuple[str, str], Dict]:
        """Load existing experiment results from files"""
        results = {}
        
        for api_dir in self.results_dir.iterdir():
            if api_dir.is_dir():
                api_name = api_dir.name.title()
                
                # Find all metrics files
                for metrics_file in api_dir.glob("metrics_*.json"):
                    # Extract dataset name from filename
                    dataset_name = metrics_file.stem.replace("metrics_", "") + ".csv"
                    
                    try:
                        # Load metrics
                        with open(metrics_file, 'r', encoding='utf-8') as f:
                            metrics = json.load(f)
                        
                        # Load graded data if exists
                        graded_file = metrics_file.parent / f"results_graded_{metrics_file.stem.replace('metrics_', '')}.csv"
                        graded_df = pd.DataFrame()
                        if graded_file.exists():
                            graded_df = pd.read_csv(graded_file)
                        
                        results[(api_name, dataset_name)] = {
                            "success": True,
                            "metrics": metrics,
                            "graded_data": graded_df,
                            "loaded_from_cache": True
                        }
                        
                    except Exception as e:
                        print(f"Error loading {metrics_file}: {e}")
                        continue
        
        return results
    
    def generate_cross_model_report(self) -> Optional[str]:
        """Generate cross-model comparison report"""
        try:
            # Update cross_model_comparison.py to use new paths
            result = subprocess.run(
                "python scripts/cross_model_comparison.py",
                shell=True, capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                report_file = "cross_model_comparison_report.txt"
                if os.path.exists(report_file):
                    with open(report_file, 'r', encoding='utf-8') as f:
                        return f.read()
            
            return None
        except Exception as e:
            print(f"Error generating report: {e}")
            return None
    
    def cleanup_old_results(self):
        """Clean up old result files outside data/ folder"""
        old_dirs = ["ollama", "ollama2", "openai", "openai2", "deepseek", "gemini"]
        
        for old_dir in old_dirs:
            if os.path.exists(old_dir) and os.path.isdir(old_dir):
                try:
                    import shutil
                    shutil.rmtree(old_dir)
                    print(f"Cleaned up old directory: {old_dir}")
                except Exception as e:
                    print(f"Warning: Could not remove {old_dir}: {e}")

def main():
    """Test the experiment runner"""
    runner = ExperimentRunner()
    
    print("Available datasets:", runner.get_available_datasets())
    print("API availability:", runner.check_api_availability())
    
    # Load existing results
    existing = runner.load_existing_results()
    print(f"Found {len(existing)} existing results")
    
    for (api, dataset), result in existing.items():
        print(f"  {api} on {dataset}: {result['metrics'].get('n_questions', 0)} questions")

if __name__ == "__main__":
    main()