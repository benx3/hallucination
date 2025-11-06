#!/usr/bin/env python3
"""
Run comprehensive experiments with all available APIs
Generates fresh results for dashboard display
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import json
from src.api_runner import APIRunner
from src.evaluator import HallucinationEvaluator
from pathlib import Path
import time

def run_comprehensive_experiments():
    """Run experiments with all available APIs on scientific facts dataset"""
    
    print("🚀 Starting comprehensive experiments...")
    
    # Load config
    with open('configs/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Load dataset
    dataset_path = 'data/scientific_facts_basic.csv'
    df = pd.read_csv(dataset_path)
    
    # Use first 20 questions for faster testing
    df_test = df.head(20).copy()
    print(f"📊 Using {len(df_test)} questions for testing")
    
    # APIs to test
    apis_to_test = [
        ("openai", "gpt-4o-mini"),
        ("gemini", "gemini-2.5-flash"),  # Fixed model
        ("deepseek", "deepseek-chat"),
        ("ollama", "llama3.2")
    ]
    
    evaluator = HallucinationEvaluator()
    
    for api_name, model_name in apis_to_test:
        print(f"\n🔄 Testing {api_name.upper()} with {model_name}...")
        
        try:
            # Check if API is configured
            if api_name not in config['apis'] or not config['apis'][api_name].get('enabled', False):
                print(f"❌ {api_name} not enabled in config")
                continue
            
            api_config = config['apis'][api_name]
            api_key = api_config.get('api_key') if api_name != 'ollama' else None
            
            # Initialize runner
            runner = APIRunner(
                provider=api_name,
                model=model_name,
                api_key=api_key,
                base_url=api_config.get('base_url')
            )
            
            # Process questions
            results = []
            for idx, row in df_test.iterrows():
                question = row['question']
                answer = row['ground_truth']
                
                print(f"  📝 Question {idx+1}/{len(df_test)}: {question[:50]}...")
                
                # Get responses
                direct_response = runner.run_direct_prompt(question)
                selfcrit_response = runner.run_self_critique_prompt(question)
                final_answer = runner.extract_final_answer(selfcrit_response)
                
                # Reconstruct the prompts used (from the default templates)
                from src.api_runner import DEFAULT_DIRECT_PROMPT, DEFAULT_SELFCRIT_PROMPT
                direct_prompt_used = DEFAULT_DIRECT_PROMPT.format(q=question)
                selfcrit_prompt_used = DEFAULT_SELFCRIT_PROMPT.format(q=question)
                
                results.append({
                    'idx': idx + 1,
                    'question': question,
                    'answer': answer,
                    'direct_answer': direct_response,
                    'selfcrit_answer': selfcrit_response,
                    'selfcrit_final_span': final_answer,
                    'api': api_name,
                    'model': model_name,
                    'gold_answer': answer,
                    'direct_prompt': direct_prompt_used,
                    'selfcrit_prompt': selfcrit_prompt_used
                })
            
            # Save results
            results_dir = Path(f"data/results/{api_name}")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            results_df = pd.DataFrame(results)
            raw_output = results_dir / "results_raw_scientific_facts.csv"
            results_df.to_csv(raw_output, index=False, encoding='utf-8')
            
            print(f"  💾 Raw results saved to {raw_output}")
            
            # Evaluate results
            print(f"  📊 Evaluating results...")
            graded_df = evaluator.grade_responses(results_df, df_test)
            metrics = evaluator.calculate_metrics(graded_df)
            
            # Save graded results and metrics
            graded_output = results_dir / "results_graded_scientific_facts.csv"
            metrics_output = results_dir / "metrics_scientific_facts.json"
            
            graded_df.to_csv(graded_output, index=False, encoding='utf-8')
            
            with open(metrics_output, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            print(f"  📈 Results:")
            print(f"     Direct - Correct: {metrics['direct']['correct_rate']:.1%}, Hallucination: {metrics['direct']['hallucination_rate']:.1%}")
            print(f"     Self-critique - Correct: {metrics['selfcrit']['correct_rate']:.1%}, Hallucination: {metrics['selfcrit']['hallucination_rate']:.1%}")
            
            # Generate Word report
            report_output = results_dir / f"report_scientific_facts.docx"
            evaluator.generate_word_report(graded_df, metrics, str(report_output))
            print(f"  📄 Report generated: {report_output}")
            
            print(f"  ✅ {api_name.upper()} completed successfully!")
            
        except Exception as e:
            print(f"  ❌ Error with {api_name}: {e}")
            continue
        
        # Small delay between APIs
        time.sleep(2)
    
    print("\n🎉 All experiments completed!")
    print("\n📋 Summary:")
    print("  Results saved in data/results/{api}/")
    print("  Launch the dashboard to view comprehensive analysis: python -m streamlit run ui/app.py")

if __name__ == "__main__":
    run_comprehensive_experiments()