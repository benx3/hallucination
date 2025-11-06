#!/usr/bin/env python3
"""
Fresh experiment runner to test all APIs with scientific facts dataset
Use this after clearing old results - runs with fixed APIRunner
"""

import os
import sys
import subprocess
from pathlib import Path

def run_fresh_experiments():
    """Run experiments for all available APIs with scientific facts"""
    print("🚀 FRESH EXPERIMENT RUNNER - Fixed APIRunner")
    print("=" * 55)
    print("Dataset: scientific_facts_basic.csv (109 questions)")
    print("APIs: OpenAI, DeepSeek, Gemini, Ollama")
    print("=" * 55)
    
    # APIs configuration
    apis = {
        "ollama": {
            "model": "llama3.2",
            "env_key": None,
            "base_url": "http://localhost:11434"
        },
        "openai": {
            "model": "gpt-4o-mini", 
            "env_key": "OPENAI_API_KEY",
            "base_url": None
        },
        "deepseek": {
            "model": "deepseek-chat",
            "env_key": "DEEPSEEK_API_KEY", 
            "base_url": "https://api.deepseek.com/v1"
        },
        "gemini": {
            "model": "gemini-1.5-flash",
            "env_key": "GOOGLE_API_KEY",
            "base_url": None
        }
    }
    
    dataset = "scientific_facts_basic.csv"
    success_count = 0
    total_apis = len(apis)
    
    print(f"\n📊 Running experiments with {dataset}...")
    
    for api_name, config in apis.items():
        print(f"\n🤖 {api_name.upper()} - {config['model']}")
        print("-" * 30)
        
        # Check if API key is available (skip if not configured)
        if config["env_key"] and not os.getenv(config["env_key"]):
            print(f"  ⚠️ Skipping {api_name} - API key not configured")
            continue
        
        # For Ollama, check if it's running
        if api_name == "ollama":
            try:
                import requests
                requests.get("http://localhost:11434/api/tags", timeout=2)
            except:
                print(f"  ⚠️ Skipping {api_name} - Ollama not running")
                continue
        
        # Set environment variables
        env = os.environ.copy()
        env["API_PROVIDER"] = api_name
        env["MODEL_NAME"] = config["model"]
        env["INPUT_CSV"] = f"data/{dataset}"
        env["OUT_CSV"] = f"data/results/{api_name}/results_raw_{dataset.replace('.csv', '')}.csv"
        
        if config["base_url"]:
            env["BASE_URL"] = config["base_url"]
        
        try:
            # Step 1: Run inference
            print(f"  🔄 Running inference...")
            result = subprocess.run(
                [sys.executable, "src/api_runner.py"],
                env=env,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                print(f"  ✅ Inference completed")
                
                # Step 2: Run evaluation
                print(f"  📊 Running evaluation...")
                eval_result = subprocess.run(
                    [sys.executable, "src/evaluator.py"],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minutes timeout
                )
                
                if eval_result.returncode == 0:
                    print(f"  ✅ Evaluation completed")
                    success_count += 1
                else:
                    print(f"  ❌ Evaluation failed")
                    if eval_result.stderr:
                        print(f"      Error: {eval_result.stderr[:200]}...")
            else:
                print(f"  ❌ Inference failed")
                if result.stderr:
                    print(f"      Error: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            print(f"  ⏰ Timeout for {api_name}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n📊 EXPERIMENT SUMMARY")
    print("=" * 30)
    print(f"Completed: {success_count}/{total_apis} APIs")
    
    if success_count > 0:
        print(f"\n📈 Generating cross-model comparison...")
        try:
            result = subprocess.run(
                [sys.executable, "scripts/cross_model_comparison.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"  ✅ Cross-model comparison completed")
                print(f"  📄 Reports generated:")
                print(f"    - cross_model_comparison_report.txt")
                print(f"    - model_comparison_summary.csv") 
                print(f"    - cross_model_comparison.png")
            else:
                print(f"  ❌ Cross-model comparison failed")
                
        except Exception as e:
            print(f"  ❌ Cross-model comparison error: {e}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  • View results in UI: http://localhost:8508")
    print(f"  • Check data/results/ for CSV files")
    print(f"  • Run python main.py for interactive menu")
    
    return success_count > 0

if __name__ == "__main__":
    print("🧪 Starting fresh experiments with fixed APIRunner...")
    print("📋 Make sure you have:")
    print("  • API keys configured in configs/config.json")
    print("  • Ollama running (if using Ollama)")
    print("  • Internet connection (for cloud APIs)")
    print()
    
    input("Press Enter to continue...")
    
    success = run_fresh_experiments()
    
    if success:
        print(f"\n🎉 Experiments completed successfully!")
    else:
        print(f"\n⚠️ No experiments completed - check API configuration")
    
    sys.exit(0 if success else 1)