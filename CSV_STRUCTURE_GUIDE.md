# 📊 Cấu trúc CSV Results Graded - Bảng Thông Tin Chi Tiết

## 🗂️ Thông tin cơ bản

| Trường | Mô tả | Ví dụ |
|--------|-------|-------|
| **idx** | Chỉ số thứ tự của câu hỏi | 0, 1, 2, 3, ... |
| **question** | Câu hỏi gốc từ dataset | "Tốc độ ánh sáng trong chân không là bao nhiêu?" |
| **api** | API provider đã sử dụng | openai, deepseek, gemini, ollama |
| **model** | Tên model cụ thể | gpt-4o-mini, deepseek-chat, gemini-pro, llama3.2 |
| **gold_answer** | Câu trả lời đúng (ground truth) | "299,792,458 m/s" hoặc "3×10^8 m/s" |

## 🤖 Câu trả lời từ mô hình

| Trường | Mô tả | Chi tiết |
|--------|-------|----------|
| **answer** | Câu trả lời gốc từ model | Có thể là direct hoặc selfcrit response |
| **direct_answer** | Câu trả lời từ direct prompting | Response từ prompt đơn giản: "Trả lời ngắn gọn..." |
| **selfcrit_answer** | Câu trả lời từ self-critique prompting | Response từ prompt 3 bước với đầy đủ reasoning |
| **selfcrit_final_span** | Phần final answer được extract | Chỉ phần "Bước 3 - Cuối cùng" từ selfcrit_answer |

### 🔍 Chi tiết Self-Critique Structure:
```
selfcrit_answer format:
**Bước 1 — Nháp**: [Câu trả lời ban đầu]
**Bước 2 — Tự kiểm**: [Quá trình tự phê phán] 
**Bước 3 — Cuối cùng**: [Câu trả lời cuối cùng]

selfcrit_final_span: Chỉ extract phần "Bước 3"
```

## ✅ Đánh giá Direct Prompting

| Trường | Định nghĩa | Giá trị | Logic |
|--------|------------|---------|-------|
| **direct_correct** | Câu trả lời direct có đúng không? | True/False | So sánh direct_answer với gold_answer |
| **direct_uncertain** | Mô hình có thể hiện uncertainty không? | True/False | Tìm patterns: "không chắc", "không biết", "uncertain" |
| **direct_hallucination** | Có xảy ra hallucination không? | True/False | `NOT correct AND NOT uncertain` |

### 📋 Logic Hallucination Detection:
```python
direct_hallucination = (not direct_correct) and (not direct_uncertain)
```

**Ý nghĩa**: Hallucination = **Sai + Tự tin** (confident but wrong)

## 🔄 Đánh giá Self-Critique Prompting

| Trường | Định nghĩa | Giá trị | Logic |
|--------|------------|---------|-------|
| **selfcrit_correct** | Câu trả lời self-critique có đúng không? | True/False | So sánh selfcrit_final_span với gold_answer |
| **selfcrit_uncertain** | Có thể hiện uncertainty không? | True/False | Tìm uncertainty patterns trong selfcrit_final_span |
| **selfcrit_hallucination** | Có hallucination không? | True/False | `NOT correct AND NOT uncertain` |

## 📊 Bảng So Sánh Metrics

| Metric Type | Direct | Self-Critique | So sánh |
|-------------|--------|---------------|---------|
| **Correctness** | direct_correct | selfcrit_correct | Tỷ lệ câu trả lời đúng |
| **Uncertainty** | direct_uncertain | selfcrit_uncertain | Khả năng nhận biết không chắc chắn |
| **Hallucination** | direct_hallucination | selfcrit_hallucination | Tỷ lệ "sai + tự tin" (cần giảm) |

## 🎯 Mục tiêu nghiên cứu

| Research Question | Hypothesis | Đo lường |
|-------------------|------------|----------|
| Self-critique có giảm hallucination? | selfcrit_hallucination < direct_hallucination | Compare rates |
| Self-critique có tăng uncertainty detection? | selfcrit_uncertain > direct_uncertain | Compare rates |
| Self-critique có cải thiện correctness? | selfcrit_correct > direct_correct | Compare rates |

## 📈 Performance Analysis

### Composite Score Calculation:
```python
# Trong analyze_models.py
composite_score = (
    correctness_rate * 40 +      # 40% weight
    uncertainty_rate * 30 +      # 30% weight  
    (1 - hallucination_rate) * 30  # 30% weight (inverted)
)
```

### Current Rankings (Real Data):
1. **🥇 Gemini Pro**: 56.2/100
2. **🥈 OpenAI GPT-4**: 49.7/100  
3. **🥉 DeepSeek**: 49.6/100
4. **🏁 Ollama**: 35.2/100

## 🔍 Analysis Examples

### Case Study: Hallucination Detection
```csv
idx,question,api,direct_correct,direct_uncertain,direct_hallucination,selfcrit_correct,selfcrit_uncertain,selfcrit_hallucination
0,"Tốc độ ánh sáng?",openai,False,False,True,True,False,False
```

**Interpretation**:
- Direct: Sai + Tự tin → **Hallucination** ❌
- Self-Critique: Đúng + Tự tin → **Good Answer** ✅
- **Improvement**: Self-critique giảm được hallucination

### Case Study: Uncertainty Detection  
```csv
idx,question,api,direct_correct,direct_uncertain,direct_hallucination,selfcrit_correct,selfcrit_uncertain,selfcrit_hallucination
1,"Câu hỏi khó",gemini,False,False,True,False,True,False
```

**Interpretation**:
- Direct: Sai + Tự tin → **Hallucination** ❌
- Self-Critique: Sai + Không chắc → **Honest Uncertainty** ✅
- **Improvement**: Self-critique tăng uncertainty detection

## 💡 Key Insights

1. **Hallucination = Confident + Wrong**: Chính xác nhưng không honest về uncertainty
2. **Self-Critique Benefit**: Quá trình 3 bước giúp model reflect và honest hơn
3. **Model Differences**: Gemini benefit nhiều nhất từ self-critique, Ollama ít nhất
4. **Dataset Variation**: Math/Science có improvement khác với general knowledge

---

**Tóm tắt**: CSV graded chứa đầy đủ thông tin để so sánh hiệu quả của Direct vs Self-Critique prompting trong việc giảm hallucination và tăng uncertainty detection. 📊