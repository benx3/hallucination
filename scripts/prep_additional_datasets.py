# prep_additional_datasets.py
# Chuẩn bị 2 dataset mới để test hallucination patterns
# REQUIRE: pip install datasets pandas

import pandas as pd
from datasets import load_dataset
import random
import os

def prepare_natural_questions(sample_size=50, seed=42):
    """Chuẩn bị Natural Questions dataset - factual Q&A"""
    print("Đang tải Natural Questions dataset...")
    
    # Load validation split (smaller)
    dataset = load_dataset("google-research-datasets/natural_questions", "default", split="validation")
    
    random.seed(seed)
    
    records = []
    sampled_indices = random.sample(range(len(dataset)), min(sample_size * 3, len(dataset)))
    
    for idx in sampled_indices[:sample_size]:
        item = dataset[idx]
        question = item['question']
        
        # Tìm short answer nếu có
        annotations = item['annotations']
        short_answer = None
        
        for annotation in annotations:
            if annotation['short_answers']:
                short_answer_span = annotation['short_answers'][0]
                start = short_answer_span['start_token']
                end = short_answer_span['end_token']
                tokens = item['document']['tokens']
                answer_tokens = tokens[start:end]
                short_answer = ' '.join([token['token'] for token in answer_tokens])
                break
        
        if short_answer and len(short_answer.strip()) > 0:
            records.append({
                'question': question,
                'ground_truth': short_answer.strip()
            })
            
        if len(records) >= sample_size:
            break
    
    df = pd.DataFrame(records)
    df.to_csv('natural_questions_50.csv', index=False, encoding='utf-8')
    print(f"Đã tạo natural_questions_50.csv với {len(df)} câu hỏi")
    return df

def prepare_fever_dataset(sample_size=50, seed=42):
    """Chuẩn bị FEVER dataset - fact verification"""
    print("Đang tải FEVER dataset...")
    
    try:
        dataset = load_dataset("fever", "v1.0", split="paper_dev")
    except:
        # Backup: sử dụng dataset khác nếu FEVER không available
        print("FEVER không khả dụng, chuyển sang SQuAD...")
        return prepare_squad_dataset(sample_size, seed)
    
    random.seed(seed)
    
    records = []
    sampled_indices = random.sample(range(len(dataset)), min(sample_size * 2, len(dataset)))
    
    for idx in sampled_indices:
        item = dataset[idx]
        claim = item['claim']
        label = item['label']
        
        # Chỉ lấy SUPPORTS và REFUTES claims
        if label in ['SUPPORTS', 'REFUTES']:
            evidence = item.get('evidence', [])
            
            # Tạo câu hỏi dạng "Is this claim true?"
            question = f"Nhận định sau đây có đúng không: {claim}"
            ground_truth = "Đúng" if label == 'SUPPORTS' else "Sai"
            
            records.append({
                'question': question,
                'ground_truth': ground_truth
            })
            
        if len(records) >= sample_size:
            break
    
    df = pd.DataFrame(records)
    df.to_csv('fever_claims_50.csv', index=False, encoding='utf-8')
    print(f"Đã tạo fever_claims_50.csv với {len(df)} câu hỏi")
    return df

def prepare_squad_dataset(sample_size=50, seed=42):
    """Backup: SQuAD dataset"""
    print("Đang tải SQuAD dataset...")
    
    dataset = load_dataset("squad", split="validation")
    random.seed(seed)
    
    records = []
    sampled_indices = random.sample(range(len(dataset)), min(sample_size * 2, len(dataset)))
    
    for idx in sampled_indices:
        item = dataset[idx]
        question = item['question']
        answers = item['answers']['text']
        
        if answers and len(answers[0].strip()) > 0:
            records.append({
                'question': question,
                'ground_truth': answers[0].strip()
            })
            
        if len(records) >= sample_size:
            break
    
    df = pd.DataFrame(records)
    df.to_csv('squad_50.csv', index=False, encoding='utf-8')
    print(f"Đã tạo squad_50.csv với {len(df)} câu hỏi")
    return df

def main():
    print("=== Chuẩn bị dataset bổ sung cho nghiên cứu hallucination ===")
    
    # Dataset 1: Natural Questions (factual QA)
    try:
        nq_df = prepare_natural_questions()
        print(f"✓ Natural Questions: {len(nq_df)} câu")
    except Exception as e:
        print(f"Lỗi khi tải Natural Questions: {e}")
        print("Chuyển sang SQuAD...")
        nq_df = prepare_squad_dataset()
    
    # Dataset 2: FEVER (fact verification) 
    try:
        fever_df = prepare_fever_dataset()
        print(f"✓ FEVER/Claims: {len(fever_df)} câu")
    except Exception as e:
        print(f"Lỗi khi tải FEVER: {e}")
        print("Tạo dataset science facts đơn giản...")
        
        # Fallback: tạo dataset khoa học đơn giản
        science_facts = [
            ("Ánh sáng có thể di chuyển trong chân không không?", "Có"),
            ("Trái đất quay quanh mặt trời hay ngược lại?", "Trái đất quay quanh mặt trời"),
            ("Nước sôi ở nhiệt độ bao nhiêu độ C ở áp suất tiêu chuẩn?", "100 độ C"),
            ("DNA có cấu trúc như thế nào?", "Cấu trúc xoắn kép"),
            ("Ánh sáng có tính chất sóng và hạt không?", "Có"),
        ] * 10  # Lặp để có đủ 50 câu
        
        science_df = pd.DataFrame(science_facts[:50], columns=['question', 'ground_truth'])
        science_df.to_csv('science_facts_50.csv', index=False, encoding='utf-8')
        print(f"✓ Science Facts: {len(science_df)} câu")
    
    print("\n=== Hoàn thành chuẩn bị dataset ===")
    print("Các file đã tạo:")
    for file in ['natural_questions_50.csv', 'fever_claims_50.csv', 'squad_50.csv', 'science_facts_50.csv']:
        if os.path.exists(file):
            print(f"  - {file}")

if __name__ == "__main__":
    main()