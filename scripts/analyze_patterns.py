# analyze_hallucination_patterns.py
# Phân tích patterns trong câu hỏi và prompt dẫn đến hallucination cao
# REQUIRE: pip install pandas numpy matplotlib seaborn nltk

import pandas as pd
import numpy as np
import re
import os
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Không có matplotlib/seaborn - bỏ qua việc vẽ biểu đồ")

# Pattern định dạng để phân tích
QUESTION_PATTERNS = {
    'wh_questions': [r'\b(ai|gì|nào|đâu|khi|tại sao|như thế nào|bao nhiêu)\b'],
    'yes_no': [r'\b(có|không|phải|đúng)\b.*\?'],
    'superlatives': [r'\b(nhất|đầu tiên|cuối cùng|lớn nhất|nhỏ nhất|cao nhất)\b'],
    'specific_numbers': [r'\b\d{4}\b', r'\b\d+\s*(năm|tháng|ngày)\b'],
    'technical_terms': [r'\b(thuật toán|công thức|phân tử|gen|virus|protein)\b'],
    'proper_nouns': [r'\b[A-Z][a-z]+(\s+[A-Z][a-z]+)*\b'],
    'comparison': [r'\b(hơn|nhỏ hơn|lớn hơn|nhanh hơn|so với)\b'],
    'temporal': [r'\b(trước|sau|trong|từ|đến|kể từ)\b.*\b(năm|thời|thế kỷ)\b']
}

def extract_question_features(question: str) -> Dict[str, int]:
    """Trích xuất features từ câu hỏi"""
    features = {}
    question_lower = question.lower()
    
    # Độ dài câu hỏi
    features['length'] = len(question)
    features['word_count'] = len(question.split())
    
    # Patterns
    for pattern_name, regexes in QUESTION_PATTERNS.items():
        features[pattern_name] = sum(
            len(re.findall(regex, question_lower, re.IGNORECASE)) 
            for regex in regexes
        )
    
    # Có dấu hỏi không
    features['has_question_mark'] = 1 if '?' in question else 0
    
    # Độ phức tạp câu (số lượng từ nối)
    conjunctions = ['và', 'hoặc', 'nhưng', 'tuy nhiên', 'ngoài ra', 'bên cạnh']
    features['complexity'] = sum(
        question_lower.count(conj) for conj in conjunctions
    )
    
    return features

def analyze_hallucination_by_patterns(graded_csv: str) -> Dict:
    """Phân tích mối quan hệ giữa patterns và hallucination rates"""
    df = pd.read_csv(graded_csv)
    
    # Trích xuất features cho mỗi câu hỏi
    features_list = []
    for _, row in df.iterrows():
        features = extract_question_features(row['question'])
        features['direct_hallucination'] = row['direct_hallucination']
        features['selfcrit_hallucination'] = row['selfcrit_hallucination']
        features['question'] = row['question']
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    
    # Phân tích correlation
    pattern_analysis = {}
    
    for pattern in QUESTION_PATTERNS.keys():
        if pattern in features_df.columns:
            # Questions có pattern này
            has_pattern = features_df[features_df[pattern] > 0]
            no_pattern = features_df[features_df[pattern] == 0]
            
            if len(has_pattern) > 0 and len(no_pattern) > 0:
                pattern_analysis[pattern] = {
                    'count_with_pattern': len(has_pattern),
                    'count_without_pattern': len(no_pattern),
                    'direct_hallu_with': has_pattern['direct_hallucination'].mean(),
                    'direct_hallu_without': no_pattern['direct_hallucination'].mean(),
                    'selfcrit_hallu_with': has_pattern['selfcrit_hallucination'].mean(),
                    'selfcrit_hallu_without': no_pattern['selfcrit_hallucination'].mean(),
                }
                
                # Risk ratio
                if no_pattern['direct_hallucination'].mean() > 0:
                    pattern_analysis[pattern]['direct_risk_ratio'] = (
                        has_pattern['direct_hallucination'].mean() / 
                        no_pattern['direct_hallucination'].mean()
                    )
                else:
                    pattern_analysis[pattern]['direct_risk_ratio'] = float('inf')
    
    return pattern_analysis, features_df

def identify_high_risk_questions(features_df: pd.DataFrame, threshold=0.7) -> List[Dict]:
    """Tìm các câu hỏi có risk cao gây hallucination"""
    high_risk = features_df[
        (features_df['direct_hallucination'] == 1) | 
        (features_df['selfcrit_hallucination'] == 1)
    ]
    
    risk_questions = []
    for _, row in high_risk.iterrows():
        risk_factors = []
        for pattern in QUESTION_PATTERNS.keys():
            if row.get(pattern, 0) > 0:
                risk_factors.append(pattern)
        
        risk_questions.append({
            'question': row['question'],
            'direct_hallu': row['direct_hallucination'],
            'selfcrit_hallu': row['selfcrit_hallucination'],
            'risk_factors': risk_factors,
            'word_count': row.get('word_count', 0),
            'complexity': row.get('complexity', 0)
        })
    
    return risk_questions

def generate_improved_prompts() -> Dict[str, str]:
    """Tạo các phiên bản prompt cải tiến để giảm hallucination"""
    improved_prompts = {
        'conservative': (
            "Bạn là trợ lý fact-checking cẩn thận. Chỉ trả lời khi hoàn toàn chắc chắn. "
            "Nếu có bất kỳ nghi ngờ nào, hãy nói 'Tôi không chắc chắn về thông tin này'.\n"
            "Câu hỏi: {q}"
        ),
        
        'evidence_based': (
            "Trả lời dựa trên kiến thức được xác minh. Nêu rõ mức độ tin cậy của bạn. "
            "Sử dụng format: [Mức độ tin cậy: Cao/Trung bình/Thấp] + Câu trả lời.\n"
            "Câu hỏi: {q}"
        ),
        
        'step_by_step': (
            "Phân tích câu hỏi theo các bước:\n"
            "1. Xác định thông tin cần thiết\n"
            "2. Đánh giá kiến thức hiện có\n"
            "3. Đưa ra câu trả lời hoặc thừa nhận không biết\n"
            "Câu hỏi: {q}"
        ),
        
        'calibrated': (
            "Trả lời với xác suất tin cậy. Format: [Tin cậy X%] + Câu trả lời. "
            "Chỉ trả lời khi tin cậy ≥80%. Dưới 80% thì nói 'Không đủ tin cậy để trả lời'.\n"
            "Câu hỏi: {q}"
        )
    }
    
    return improved_prompts

def main():
    print("=== Phân tích Patterns Gây Hallucination ===")
    
    # Tìm các file results_graded.csv
    result_dirs = ['ollama', 'ollama2', 'openai', 'openai2']
    all_analyses = {}
    
    for result_dir in result_dirs:
        graded_file = os.path.join(result_dir, 'results_graded.csv')
        if os.path.exists(graded_file):
            print(f"\nPhân tích {result_dir}...")
            pattern_analysis, features_df = analyze_hallucination_by_patterns(graded_file)
            
            all_analyses[result_dir] = {
                'patterns': pattern_analysis,
                'features': features_df
            }
            
            # Tìm câu hỏi high-risk
            high_risk = identify_high_risk_questions(features_df)
            print(f"  Tìm thấy {len(high_risk)} câu hỏi high-risk")
            
            # Lưu phân tích
            output_file = os.path.join(result_dir, 'pattern_analysis.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"PHÂN TÍCH PATTERNS - {result_dir.upper()}\n")
                f.write("="*50 + "\n\n")
                
                f.write("PATTERNS VÀ HALLUCINATION RATES:\n")
                for pattern, stats in pattern_analysis.items():
                    f.write(f"\n{pattern}:\n")
                    f.write(f"  - Có pattern: {stats['direct_hallu_with']:.3f} (direct), {stats['selfcrit_hallu_with']:.3f} (selfcrit)\n")
                    f.write(f"  - Không có: {stats['direct_hallu_without']:.3f} (direct), {stats['selfcrit_hallu_without']:.3f} (selfcrit)\n")
                    f.write(f"  - Risk ratio: {stats.get('direct_risk_ratio', 'N/A'):.2f}\n")
                
                f.write(f"\n\nCÂU HỎI HIGH-RISK ({len(high_risk)} câu):\n")
                for i, q in enumerate(high_risk[:10]):  # Top 10
                    f.write(f"\n{i+1}. {q['question']}\n")
                    f.write(f"   Risk factors: {', '.join(q['risk_factors'])}\n")
                    f.write(f"   Hallucination: Direct={q['direct_hallu']}, SelfCrit={q['selfcrit_hallu']}\n")
    
    # Tạo improved prompts
    improved_prompts = generate_improved_prompts()
    with open('improved_prompts.py', 'w', encoding='utf-8') as f:
        f.write("# Improved prompt templates để giảm hallucination\n\n")
        f.write("IMPROVED_PROMPTS = {\n")
        for name, template in improved_prompts.items():
            f.write(f"    '{name}': (\n")
            f.write(f"        \"{template}\"\n")
            f.write(f"    ),\n\n")
        f.write("}\n")
    
    print(f"\n✓ Phân tích hoàn thành!")
    print(f"✓ Đã tạo improved_prompts.py với {len(improved_prompts)} prompt templates")
    
    # Vẽ biểu đồ nếu có thể
    if HAS_PLOTTING and all_analyses:
        plot_hallucination_analysis(all_analyses)

def plot_hallucination_analysis(all_analyses: Dict):
    """Vẽ biểu đồ phân tích hallucination"""
    if not HAS_PLOTTING:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Hallucination Pattern Analysis', fontsize=16)
    
    # Tổng hợp data từ tất cả models
    all_patterns = defaultdict(list)
    for model_name, analysis in all_analyses.items():
        for pattern, stats in analysis['patterns'].items():
            all_patterns[pattern].append({
                'model': model_name,
                'direct_with': stats['direct_hallu_with'],
                'direct_without': stats['direct_hallu_without'],
                'risk_ratio': stats.get('direct_risk_ratio', 1.0)
            })
    
    # Plot 1: Risk ratios by pattern
    patterns = list(all_patterns.keys())
    avg_risk_ratios = [
        np.mean([stat['risk_ratio'] for stat in all_patterns[p] if stat['risk_ratio'] != float('inf')])
        for p in patterns
    ]
    
    axes[0,0].barh(patterns, avg_risk_ratios)
    axes[0,0].set_xlabel('Average Risk Ratio')
    axes[0,0].set_title('Risk Ratios by Question Pattern')
    axes[0,0].axvline(x=1.0, color='red', linestyle='--', label='Baseline')
    
    plt.tight_layout()
    plt.savefig('hallucination_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Đã lưu biểu đồ phân tích: hallucination_analysis.png")

if __name__ == "__main__":
    main()