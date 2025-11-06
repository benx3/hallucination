# test_improved_prompts.py
# Test các prompt templates cải tiến để giảm hallucination
# REQUIRE: pip install openai pandas python-dotenv

import os
import pandas as pd
from typing import List, Dict
from openai import OpenAI
import time

# API Configuration - có thể chuyển đổi giữa các providers
API_PROVIDER = os.getenv("API_PROVIDER", "openai")  # openai, deepseek, gemini
API_KEY = os.getenv("API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
INPUT_CSV = os.getenv("INPUT_CSV", "data/scientific_facts_basic.csv")
OUT_CSV = os.getenv("OUT_CSV", "improved_prompts/results_raw.csv")
TIMEOUT_S = int(os.getenv("TIMEOUT_S", "120"))

# Improved prompt templates
IMPROVED_PROMPTS = {
    'baseline_direct': (
        "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn. "
        "Nếu không chắc chắn, hãy nói 'không chắc'.\n"
        "Câu hỏi: {q}"
    ),
    
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
    ),
    
    'meta_cognitive': (
        "Trước khi trả lời, hãy tự hỏi: 'Liệu tôi có thực sự biết điều này không?'. "
        "Nếu có nghi ngờ, hãy thành thật thừa nhận. Độ chính xác quan trọng hơn việc có câu trả lời.\n"
        "Câu hỏi: {q}"
    ),
    
    'domain_aware': (
        "Phân loại câu hỏi theo domain (khoa học, lịch sử, địa lý, v.v.) và đánh giá "
        "mức độ chuyên môn cần thiết. Nếu vượt quá khả năng, hãy thẳng thắn nói không biết.\n"
        "Câu hỏi: {q}"
    )
}

def setup_client():
    """Setup API client dựa trên provider"""
    if API_PROVIDER == "openai":
        return OpenAI(api_key=API_KEY)
    elif API_PROVIDER == "deepseek":
        return OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    else:
        raise ValueError(f"Provider {API_PROVIDER} chưa được support trong script này")

def chat_once(client: OpenAI, messages: List[Dict[str, str]]) -> str:
    """Gửi request tới API"""
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            timeout=TIMEOUT_S,
            temperature=0.1
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"Lỗi API: {e}")
        return f"[LỖI API: {str(e)}]"

def test_all_prompts(questions_df: pd.DataFrame) -> pd.DataFrame:
    """Test tất cả prompt templates trên dataset"""
    client = setup_client()
    
    results = []
    total_questions = len(questions_df)
    
    print(f"Testing {len(IMPROVED_PROMPTS)} prompt templates trên {total_questions} câu hỏi...")
    
    for i, row in questions_df.iterrows():
        question = row["question"]
        result_row = {
            "idx": i + 1,
            "question": question
        }
        
        # Test mỗi prompt template
        for prompt_name, template in IMPROVED_PROMPTS.items():
            prompt = template.format(q=question)
            answer = chat_once(client, [{"role": "user", "content": prompt}])
            result_row[f"{prompt_name}_answer"] = answer
            
            print(f"[{i+1:02d}/{total_questions}] {prompt_name}: OK")
            time.sleep(0.5)  # Rate limiting
        
        results.append(result_row)
    
    return pd.DataFrame(results)

def extract_confidence_indicators(answer: str) -> Dict[str, float]:
    """Trích xuất indicators về confidence từ câu trả lời"""
    indicators = {
        'explicit_uncertainty': 0.0,
        'hedge_words': 0.0,
        'confidence_percentage': None
    }
    
    answer_lower = answer.lower()
    
    # Explicit uncertainty phrases
    uncertainty_phrases = [
        'không chắc', 'không rõ', 'không biết', 'không đủ tin cậy',
        'có thể', 'dường như', 'có vẻ', 'khả năng', 'ước tính'
    ]
    
    for phrase in uncertainty_phrases:
        if phrase in answer_lower:
            indicators['explicit_uncertainty'] = 1.0
            break
    
    # Hedge words
    hedge_words = ['có thể', 'thường', 'thông thường', 'đại khái', 'khoảng', 'gần như']
    hedge_count = sum(1 for word in hedge_words if word in answer_lower)
    indicators['hedge_words'] = min(hedge_count / 3.0, 1.0)  # Normalize to 0-1
    
    # Extract confidence percentage if present
    import re
    confidence_match = re.search(r'(\d+)%', answer)
    if confidence_match:
        indicators['confidence_percentage'] = float(confidence_match.group(1)) / 100.0
    
    return indicators

def analyze_prompt_effectiveness(results_df: pd.DataFrame, original_graded_csv: str = None) -> Dict:
    """Phân tích hiệu quả của các prompt templates"""
    analysis = {}
    
    for prompt_name in IMPROVED_PROMPTS.keys():
        answer_col = f"{prompt_name}_answer"
        if answer_col not in results_df.columns:
            continue
        
        # Analyze confidence indicators
        confidence_data = []
        for answer in results_df[answer_col]:
            indicators = extract_confidence_indicators(str(answer))
            confidence_data.append(indicators)
        
        confidence_df = pd.DataFrame(confidence_data)
        
        analysis[prompt_name] = {
            'uncertainty_rate': confidence_df['explicit_uncertainty'].mean(),
            'hedge_rate': confidence_df['hedge_words'].mean(),
            'avg_response_length': results_df[answer_col].astype(str).str.len().mean(),
            'total_responses': len(results_df)
        }
        
        # Nếu có confidence percentages
        if confidence_df['confidence_percentage'].notna().any():
            analysis[prompt_name]['avg_confidence'] = confidence_df['confidence_percentage'].mean()
    
    return analysis

def main():
    if not API_KEY:
        raise RuntimeError(f"Thiếu API key cho {API_PROVIDER}")
    
    # Tạo thư mục output
    os.makedirs(os.path.dirname(OUT_CSV) if os.path.dirname(OUT_CSV) else ".", exist_ok=True)
    
    # Load questions
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} questions from {INPUT_CSV}")
    
    # Test all prompts
    results_df = test_all_prompts(df)
    
    # Save raw results
    results_df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"Đã lưu kết quả raw vào {OUT_CSV}")
    
    # Analyze effectiveness
    analysis = analyze_prompt_effectiveness(results_df)
    
    # Save analysis
    analysis_file = OUT_CSV.replace('results_raw.csv', 'prompt_analysis.txt')
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write("PHÂN TÍCH HIỆU QUẢ PROMPT TEMPLATES\n")
        f.write("="*50 + "\n\n")
        
        # Sort by uncertainty rate (higher is often better for reducing hallucination)
        sorted_prompts = sorted(analysis.items(), 
                              key=lambda x: x[1]['uncertainty_rate'], reverse=True)
        
        for prompt_name, stats in sorted_prompts:
            f.write(f"{prompt_name.upper()}:\n")
            f.write(f"  - Tỷ lệ thể hiện uncertainty: {stats['uncertainty_rate']:.3f}\n")
            f.write(f"  - Tỷ lệ sử dụng hedge words: {stats['hedge_rate']:.3f}\n")
            f.write(f"  - Độ dài trung bình câu trả lời: {stats['avg_response_length']:.1f} ký tự\n")
            if 'avg_confidence' in stats:
                f.write(f"  - Mức độ tin cậy trung bình: {stats['avg_confidence']:.3f}\n")
            f.write("\n")
    
    print(f"✓ Đã lưu phân tích vào {analysis_file}")
    print(f"✓ Hoàn thành test {len(IMPROVED_PROMPTS)} prompt templates!")

if __name__ == "__main__":
    main()