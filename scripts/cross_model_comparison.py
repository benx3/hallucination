# cross_model_comparison.py
# So sánh hallucination rates giữa các LLM models (OpenAI, Ollama, DeepSeek, Gemini)
# REQUIRE: pip install pandas numpy matplotlib seaborn

import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Tuple
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
    plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'Arial Unicode MS']
except ImportError:
    HAS_PLOTTING = False
    print("Matplotlib không khả dụng - bỏ qua việc vẽ biểu đồ")

def collect_all_results() -> Dict[str, Dict]:
    """Thu thập kết quả từ tất cả model directories"""
    # Updated paths to use data/results structure
    results_base = "data/results"
    model_dirs = {
        'OpenAI GPT': ['openai'],
        'Ollama': ['ollama'], 
        'DeepSeek': ['deepseek'],
        'Gemini': ['gemini']
    }
    
    all_results = {}
    
    for model_family, dirs in model_dirs.items():
        family_results = []
        
        for dir_name in dirs:
            model_path = os.path.join(results_base, dir_name)
            if os.path.exists(model_path):
                # Look for metrics files for each dataset
                for metrics_file in os.listdir(model_path):
                    if metrics_file.startswith('metrics_') and metrics_file.endswith('.json'):
                        dataset_name = metrics_file.replace('metrics_', '').replace('.json', '')
                        
                        metrics_path = os.path.join(model_path, metrics_file)
                        graded_file = os.path.join(model_path, f'results_graded_{dataset_name}.csv')
                        
                        if os.path.exists(graded_file):
                            with open(metrics_path, 'r', encoding='utf-8') as f:
                                metrics = json.load(f)
                            
                            graded_df = pd.read_csv(graded_file)
                            
                            family_results.append({
                                'dir': f"{dir_name}_{dataset_name}",
                                'dataset': dataset_name,
                                'metrics': metrics,
                                'data': graded_df
                            })
        
        if family_results:
            all_results[model_family] = family_results
    
    return all_results

def aggregate_model_performance(all_results: Dict) -> pd.DataFrame:
    """Tạo bảng tổng hợp performance của các models"""
    summary_data = []
    
    for model_family, results_list in all_results.items():
        for result in results_list:
            metrics = result['metrics']
            
            summary_data.append({
                'Model Family': model_family,
                'Directory': result['dir'],
                'n_questions': metrics.get('n_questions', 0),
                'accuracy_direct': metrics.get('accuracy_direct', 0),
                'accuracy_selfcrit': metrics.get('accuracy_selfcrit', 0),
                'hallu_rate_direct': metrics.get('hallu_rate_direct', 0),
                'hallu_rate_selfcrit': metrics.get('hallu_rate_selfcrit', 0),
                'accuracy_gain': metrics.get('accuracy_gain', 0),
                'hallu_reduction': metrics.get('hallu_reduction', 0)
            })
    
    return pd.DataFrame(summary_data)

def analyze_question_difficulty(all_results: Dict) -> Dict:
    """Phân tích các câu hỏi khó/dễ gây hallucination across models"""
    
    # Collect all questions with their hallucination status across models
    question_analysis = defaultdict(list)
    
    for model_family, results_list in all_results.items():
        for result in results_list:
            df = result['data']
            for _, row in df.iterrows():
                question = row['question']
                question_analysis[question].append({
                    'model': f"{model_family}_{result['dir']}",
                    'direct_hallu': row['direct_hallucination'],
                    'selfcrit_hallu': row['selfcrit_hallucination'],
                    'direct_correct': row['direct_correct'],
                    'selfcrit_correct': row['selfcrit_correct']
                })
    
    # Tính difficulty score cho mỗi câu hỏi
    question_difficulty = {}
    for question, model_results in question_analysis.items():
        if len(model_results) >= 2:  # Chỉ analyze questions có ít nhất 2 model results
            total_models = len(model_results)
            total_direct_hallu = sum(r['direct_hallu'] for r in model_results)
            total_selfcrit_hallu = sum(r['selfcrit_hallu'] for r in model_results)
            
            question_difficulty[question] = {
                'n_models': total_models,
                'direct_hallu_rate': total_direct_hallu / total_models,
                'selfcrit_hallu_rate': total_selfcrit_hallu / total_models,
                'difficulty_score': (total_direct_hallu + total_selfcrit_hallu) / (2 * total_models)
            }
    
    return question_difficulty

def find_model_strengths_weaknesses(summary_df: pd.DataFrame) -> Dict:
    """Tìm điểm mạnh/yếu của từng model family"""
    analysis = {}
    
    # Group by model family và tính average
    family_stats = summary_df.groupby('Model Family').agg({
        'accuracy_direct': 'mean',
        'accuracy_selfcrit': 'mean', 
        'hallu_rate_direct': 'mean',
        'hallu_rate_selfcrit': 'mean',
        'accuracy_gain': 'mean',
        'hallu_reduction': 'mean'
    }).round(4)
    
    for model_family in family_stats.index:
        stats = family_stats.loc[model_family]
        
        strengths = []
        weaknesses = []
        
        # So sánh với average của tất cả models
        overall_avg = family_stats.mean()
        
        if stats['accuracy_direct'] > overall_avg['accuracy_direct']:
            strengths.append(f"High direct accuracy ({stats['accuracy_direct']:.3f})")
        else:
            weaknesses.append(f"Low direct accuracy ({stats['accuracy_direct']:.3f})")
        
        if stats['hallu_rate_direct'] < overall_avg['hallu_rate_direct']:
            strengths.append(f"Low hallucination rate ({stats['hallu_rate_direct']:.3f})")
        else:
            weaknesses.append(f"High hallucination rate ({stats['hallu_rate_direct']:.3f})")
        
        if stats['accuracy_gain'] > 0:
            strengths.append(f"Benefits from self-critique (+{stats['accuracy_gain']:.3f})")
        else:
            weaknesses.append(f"No improvement from self-critique ({stats['accuracy_gain']:.3f})")
        
        analysis[model_family] = {
            'stats': stats.to_dict(),
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    return analysis

def generate_comprehensive_report(all_results: Dict, summary_df: pd.DataFrame, 
                                question_difficulty: Dict, model_analysis: Dict):
    """Tạo báo cáo tổng hợp toàn diện"""
    
    report_content = []
    report_content.append("BÁOCÁO SO SÁNH HALLUCINATION GIỮA CÁC LLM")
    report_content.append("=" * 60)
    report_content.append("")
    
    # 1. Executive Summary
    report_content.append("1. TÓM TẮT TỔNG QUAN")
    report_content.append("-" * 30)
    total_models = len(summary_df)
    avg_direct_acc = summary_df['accuracy_direct'].mean()
    avg_selfcrit_acc = summary_df['accuracy_selfcrit'].mean()
    avg_hallu_reduction = summary_df['hallu_reduction'].mean()
    
    report_content.append(f"- Tổng số models tested: {total_models}")
    report_content.append(f"- Accuracy trung bình (direct): {avg_direct_acc:.3f}")
    report_content.append(f"- Accuracy trung bình (self-critique): {avg_selfcrit_acc:.3f}")
    report_content.append(f"- Hallucination reduction trung bình: {avg_hallu_reduction:.3f}")
    report_content.append("")
    
    # 2. Model Ranking
    report_content.append("2. XẾP HẠNG MODELS")
    report_content.append("-" * 30)
    
    # Rank by hallucination rate (lower is better)
    ranking = summary_df.sort_values('hallu_rate_direct')
    report_content.append("Theo tỷ lệ hallucination (thấp = tốt):")
    for i, (_, row) in enumerate(ranking.iterrows(), 1):
        report_content.append(f"{i}. {row['Model Family']} ({row['Directory']}): {row['hallu_rate_direct']:.3f}")
    
    report_content.append("")
    
    # 3. Model Strengths & Weaknesses
    report_content.append("3. ĐIỂM MẠNH & YẾU CỦA TỪNG MODEL")
    report_content.append("-" * 40)
    
    for model_family, analysis in model_analysis.items():
        report_content.append(f"\n{model_family.upper()}:")
        report_content.append("  Điểm mạnh:")
        for strength in analysis['strengths']:
            report_content.append(f"    + {strength}")
        report_content.append("  Điểm yếu:")
        for weakness in analysis['weaknesses']:
            report_content.append(f"    - {weakness}")
    
    report_content.append("")
    
    # 4. Difficult Questions
    report_content.append("4. CÂU HỎI KHÓ NHẤT (Gây hallucination cao)")
    report_content.append("-" * 50)
    
    # Sort questions by difficulty score
    sorted_questions = sorted(question_difficulty.items(), 
                            key=lambda x: x[1]['difficulty_score'], reverse=True)
    
    report_content.append("Top 10 câu hỏi khó nhất:")
    for i, (question, stats) in enumerate(sorted_questions[:10], 1):
        report_content.append(f"\n{i}. {question}")
        report_content.append(f"   Difficulty score: {stats['difficulty_score']:.3f}")
        report_content.append(f"   Tested on {stats['n_models']} models")
        report_content.append(f"   Direct hallucination rate: {stats['direct_hallu_rate']:.3f}")
        report_content.append(f"   Self-critique hallucination rate: {stats['selfcrit_hallu_rate']:.3f}")
    
    # 5. Recommendations
    report_content.append("\n\n5. KHUYẾN NGHỊ")
    report_content.append("-" * 20)
    
    best_model = ranking.iloc[0]
    worst_model = ranking.iloc[-1]
    
    report_content.append(f"- Model tốt nhất: {best_model['Model Family']} với tỷ lệ hallucination {best_model['hallu_rate_direct']:.3f}")
    report_content.append(f"- Model cần cải thiện: {worst_model['Model Family']} với tỷ lệ hallucination {worst_model['hallu_rate_direct']:.3f}")
    
    if avg_hallu_reduction > 0:
        report_content.append("- Self-critique prompting có hiệu quả tích cực")
    else:
        report_content.append("- Self-critique prompting chưa hiệu quả, cần cải thiện prompt design")
    
    # Save report
    with open('cross_model_comparison_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
    
    print("✓ Đã tạo báo cáo tổng hợp: cross_model_comparison_report.txt")

def plot_model_comparison(summary_df: pd.DataFrame, question_difficulty: Dict):
    """Vẽ biểu đồ so sánh các models"""
    if not HAS_PLOTTING:
        return
    
    # Setup matplotlib for Vietnamese
    plt.rcParams['font.size'] = 10
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Cross-Model Hallucination Analysis', fontsize=16, fontweight='bold')
    
    # 1. Accuracy Comparison
    axes[0,0].bar(range(len(summary_df)), summary_df['accuracy_direct'], 
                  alpha=0.7, label='Direct', color='lightblue')
    axes[0,0].bar(range(len(summary_df)), summary_df['accuracy_selfcrit'], 
                  alpha=0.7, label='Self-Critique', color='orange')
    axes[0,0].set_xlabel('Models')
    axes[0,0].set_ylabel('Accuracy')
    axes[0,0].set_title('Accuracy Comparison')
    axes[0,0].legend()
    axes[0,0].set_xticks(range(len(summary_df)))
    axes[0,0].set_xticklabels([f"{row['Model Family']}\n{row['Directory']}" 
                              for _, row in summary_df.iterrows()], rotation=45)
    
    # 2. Hallucination Rate Comparison
    axes[0,1].bar(range(len(summary_df)), summary_df['hallu_rate_direct'], 
                  alpha=0.7, label='Direct', color='lightcoral')
    axes[0,1].bar(range(len(summary_df)), summary_df['hallu_rate_selfcrit'], 
                  alpha=0.7, label='Self-Critique', color='darkred')
    axes[0,1].set_xlabel('Models')
    axes[0,1].set_ylabel('Hallucination Rate')
    axes[0,1].set_title('Hallucination Rate Comparison')
    axes[0,1].legend()
    axes[0,1].set_xticks(range(len(summary_df)))
    axes[0,1].set_xticklabels([f"{row['Model Family']}\n{row['Directory']}" 
                              for _, row in summary_df.iterrows()], rotation=45)
    
    # 3. Improvement from Self-Critique
    axes[0,2].bar(range(len(summary_df)), summary_df['accuracy_gain'], 
                  alpha=0.7, color='green')
    axes[0,2].axhline(y=0, color='red', linestyle='--', alpha=0.5)
    axes[0,2].set_xlabel('Models')
    axes[0,2].set_ylabel('Accuracy Gain')
    axes[0,2].set_title('Self-Critique Effectiveness')
    axes[0,2].set_xticks(range(len(summary_df)))
    axes[0,2].set_xticklabels([f"{row['Model Family']}\n{row['Directory']}" 
                              for _, row in summary_df.iterrows()], rotation=45)
    
    # 4. Question Difficulty Distribution
    difficulty_scores = [stats['difficulty_score'] for stats in question_difficulty.values()]
    axes[1,0].hist(difficulty_scores, bins=20, alpha=0.7, color='purple')
    axes[1,0].set_xlabel('Difficulty Score')
    axes[1,0].set_ylabel('Number of Questions')
    axes[1,0].set_title('Question Difficulty Distribution')
    
    # 5. Model Family Average Performance
    family_avg = summary_df.groupby('Model Family')[['accuracy_direct', 'hallu_rate_direct']].mean()
    x_pos = range(len(family_avg))
    axes[1,1].bar([x-0.2 for x in x_pos], family_avg['accuracy_direct'], 
                  width=0.4, label='Accuracy', alpha=0.7, color='lightblue')
    axes[1,1].bar([x+0.2 for x in x_pos], family_avg['hallu_rate_direct'], 
                  width=0.4, label='Hallucination Rate', alpha=0.7, color='lightcoral')
    axes[1,1].set_xlabel('Model Family')
    axes[1,1].set_ylabel('Rate')
    axes[1,1].set_title('Average Performance by Model Family')
    axes[1,1].legend()
    axes[1,1].set_xticks(x_pos)
    axes[1,1].set_xticklabels(family_avg.index, rotation=45)
    
    # 6. Scatter: Accuracy vs Hallucination
    axes[1,2].scatter(summary_df['accuracy_direct'], summary_df['hallu_rate_direct'], 
                     alpha=0.7, s=100, c='blue', label='Direct')
    axes[1,2].scatter(summary_df['accuracy_selfcrit'], summary_df['hallu_rate_selfcrit'], 
                     alpha=0.7, s=100, c='red', label='Self-Critique')
    axes[1,2].set_xlabel('Accuracy')
    axes[1,2].set_ylabel('Hallucination Rate')
    axes[1,2].set_title('Accuracy vs Hallucination Trade-off')
    axes[1,2].legend()
    
    # Add model labels
    for i, row in summary_df.iterrows():
        axes[1,2].annotate(f"{row['Model Family'][:3]}", 
                          (row['accuracy_direct'], row['hallu_rate_direct']),
                          xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('cross_model_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Đã lưu biểu đồ so sánh: cross_model_comparison.png")

def main():
    print("=== So sánh Hallucination giữa các LLM Models ===")
    
    # Collect all results
    all_results = collect_all_results()
    
    if not all_results:
        print("Không tìm thấy kết quả nào! Hãy chạy các script inference trước.")
        return
    
    print(f"Tìm thấy kết quả từ {len(all_results)} model families")
    
    # Aggregate performance
    summary_df = aggregate_model_performance(all_results)
    print(f"Tổng hợp {len(summary_df)} model runs")
    
    # Analyze question difficulty
    question_difficulty = analyze_question_difficulty(all_results)
    print(f"Phân tích {len(question_difficulty)} câu hỏi")
    
    # Find model strengths/weaknesses
    model_analysis = find_model_strengths_weaknesses(summary_df)
    
    # Generate comprehensive report
    generate_comprehensive_report(all_results, summary_df, 
                                question_difficulty, model_analysis)
    
    # Save summary data
    summary_df.to_csv('model_comparison_summary.csv', index=False, encoding='utf-8')
    print("✓ Đã lưu tổng hợp data: model_comparison_summary.csv")
    
    # Create visualizations
    if HAS_PLOTTING:
        plot_model_comparison(summary_df, question_difficulty)
    
    print("\n=== Hoàn thành so sánh cross-model ===")

if __name__ == "__main__":
    main()