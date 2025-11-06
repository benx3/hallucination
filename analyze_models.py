#!/usr/bin/env python3
"""Analyze and compare all LLM results"""

import json
import pandas as pd
from pathlib import Path
import os

def load_metrics_from_directory(api_dir):
    """Load all metrics from an API directory"""
    metrics_files = list(Path(api_dir).glob("metrics_*.json"))
    all_metrics = {}
    
    for metrics_file in metrics_files:
        dataset_name = metrics_file.stem.replace("metrics_", "")
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
                all_metrics[dataset_name] = metrics
        except Exception as e:
            print(f"Error loading {metrics_file}: {e}")
    
    return all_metrics

def analyze_all_models():
    """Analyze performance across all models and datasets"""
    results_dir = Path("data/results")
    apis = ["openai", "deepseek", "gemini", "ollama"]
    
    print("🔍 COMPREHENSIVE LLM COMPARISON ANALYSIS")
    print("=" * 60)
    
    all_results = {}
    
    for api in apis:
        api_dir = results_dir / api
        if api_dir.exists():
            print(f"\n📊 Loading {api.upper()} results...")
            all_results[api] = load_metrics_from_directory(api_dir)
        else:
            print(f"❌ No results found for {api}")
    
    # Calculate aggregate scores
    api_scores = {}
    
    for api, datasets in all_results.items():
        if not datasets:
            continue
            
        direct_correct_rates = []
        direct_hallu_rates = []
        selfcrit_correct_rates = []
        selfcrit_hallu_rates = []
        improvements = []
        
        print(f"\n🤖 {api.upper()} DETAILED RESULTS:")
        print("-" * 40)
        
        for dataset, metrics in datasets.items():
            if not metrics:
                continue
                
            direct = metrics.get('direct', {})
            selfcrit = metrics.get('selfcrit', {})
            improvement = metrics.get('improvement', {})
            
            direct_correct = direct.get('correct_rate', 0) * 100
            direct_hallu = direct.get('hallucination_rate', 0) * 100
            selfcrit_correct = selfcrit.get('correct_rate', 0) * 100
            selfcrit_hallu = selfcrit.get('hallucination_rate', 0) * 100
            
            correct_improvement = improvement.get('correct_delta', 0) * 100
            hallu_reduction = -improvement.get('hallucination_delta', 0) * 100
            
            print(f"  📝 {dataset}:")
            print(f"     Direct:     {direct_correct:5.1f}% correct, {direct_hallu:5.1f}% hallucination")
            print(f"     Self-Crit:  {selfcrit_correct:5.1f}% correct, {selfcrit_hallu:5.1f}% hallucination")
            print(f"     Improvement: {correct_improvement:+5.1f}% correct, {hallu_reduction:+5.1f}% hallu reduction")
            
            direct_correct_rates.append(direct_correct)
            direct_hallu_rates.append(direct_hallu)
            selfcrit_correct_rates.append(selfcrit_correct)
            selfcrit_hallu_rates.append(selfcrit_hallu)
            improvements.append(correct_improvement)
        
        if direct_correct_rates:
            avg_direct_correct = sum(direct_correct_rates) / len(direct_correct_rates)
            avg_direct_hallu = sum(direct_hallu_rates) / len(direct_hallu_rates)
            avg_selfcrit_correct = sum(selfcrit_correct_rates) / len(selfcrit_correct_rates)
            avg_selfcrit_hallu = sum(selfcrit_hallu_rates) / len(selfcrit_hallu_rates)
            avg_improvement = sum(improvements) / len(improvements)
            
            # Calculate composite score (higher is better)
            # Weights: correct rate (60%), hallucination reduction (30%), improvement (10%)
            composite_score = (avg_selfcrit_correct * 0.6 + 
                             (100 - avg_selfcrit_hallu) * 0.3 + 
                             (avg_improvement + 50) * 0.1)  # +50 to normalize improvement
            
            api_scores[api] = {
                'avg_direct_correct': avg_direct_correct,
                'avg_direct_hallu': avg_direct_hallu,
                'avg_selfcrit_correct': avg_selfcrit_correct,
                'avg_selfcrit_hallu': avg_selfcrit_hallu,
                'avg_improvement': avg_improvement,
                'composite_score': composite_score,
                'dataset_count': len(direct_correct_rates)
            }
            
            print(f"\n  🎯 AVERAGES:")
            print(f"     Direct:     {avg_direct_correct:5.1f}% correct, {avg_direct_hallu:5.1f}% hallucination")
            print(f"     Self-Crit:  {avg_selfcrit_correct:5.1f}% correct, {avg_selfcrit_hallu:5.1f}% hallucination")
            print(f"     Improvement: {avg_improvement:+5.1f}% correct")
            print(f"     Composite Score: {composite_score:.1f}/100")
    
    # Rank models
    print(f"\n🏆 FINAL RANKING (Based on Self-Critique Performance)")
    print("=" * 60)
    
    ranked_apis = sorted(api_scores.items(), key=lambda x: x[1]['composite_score'], reverse=True)
    
    for rank, (api, scores) in enumerate(ranked_apis, 1):
        if rank == 1:
            emoji = "🥇"
        elif rank == 2:
            emoji = "🥈"
        elif rank == 3:
            emoji = "🥉"
        else:
            emoji = "4️⃣"
            
        print(f"\n{emoji} RANK {rank}: {api.upper()}")
        print(f"   Self-Critique Accuracy: {scores['avg_selfcrit_correct']:5.1f}%")
        print(f"   Self-Critique Hallucination: {scores['avg_selfcrit_hallu']:5.1f}%")
        print(f"   Improvement over Direct: {scores['avg_improvement']:+5.1f}%")
        print(f"   Composite Score: {scores['composite_score']:.1f}/100")
        print(f"   Datasets tested: {scores['dataset_count']}")
    
    # Key insights
    print(f"\n📈 KEY INSIGHTS:")
    print("-" * 30)
    
    best_api = ranked_apis[0][0]
    worst_api = ranked_apis[-1][0]
    
    best_accuracy = max(scores['avg_selfcrit_correct'] for _, scores in ranked_apis)
    lowest_hallu = min(scores['avg_selfcrit_hallu'] for _, scores in ranked_apis)
    best_improvement = max(scores['avg_improvement'] for _, scores in ranked_apis)
    
    print(f"🎯 Best Overall: {best_api.upper()} (composite score: {ranked_apis[0][1]['composite_score']:.1f})")
    print(f"📊 Highest Accuracy: {best_accuracy:.1f}%")
    print(f"🛡️  Lowest Hallucination: {lowest_hallu:.1f}%")
    print(f"📈 Best Improvement: {best_improvement:+.1f}%")
    
    if len(ranked_apis) > 1:
        score_gap = ranked_apis[0][1]['composite_score'] - ranked_apis[1][1]['composite_score']
        print(f"🔥 Performance Gap (1st vs 2nd): {score_gap:.1f} points")

if __name__ == "__main__":
    analyze_all_models()