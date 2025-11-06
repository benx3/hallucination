
# Hướng dẫn nhanh (Ollama local)

## 1) Chuẩn bị
- Đảm bảo `ollama serve` đang chạy.
- Kéo model bạn muốn: ví dụ `ollama run llama3.1` (hoặc `qwen2`, `mistral`, ...).
- Cài thư viện Python:
```
pip install requests pandas python-docx python-dotenv
```

## 2) Dataset
- File `questions_50.csv` đã kèm 50 câu hỏi + ground_truth (tiếng Việt).

## 3) Chạy suy luận & lưu kết quả thô
```
export MODEL_NAME=llama3.1
python run_ollama_eval.py
# -> tạo results_raw.csv
```

Tuỳ chọn biến môi trường:
- `OLLAMA_HOST` (mặc định `http://localhost:11434`)
- `MODEL_NAME`
- `INPUT_CSV` (mặc định `questions_50.csv`)
- `OUT_CSV` (mặc định `results_raw.csv`)

## 4) Chấm điểm & Xuất báo cáo
```
python grade_and_report.py
# -> results_graded.csv, metrics.json, Experiment_Report.docx
```

### Cách chấm điểm (heuristic)
- **Đúng** nếu đáp án chuẩn xuất hiện trong câu trả lời (sau chuẩn hoá).
- **Hallucination** = trả lời **sai** nhưng **không** thể hiện sự **không chắc chắn** (phát hiện bằng các cụm như "không chắc", "not sure", ...).
- Đo: `accuracy_direct`, `accuracy_selfcrit`, `hallu_rate_direct`, `hallu_rate_selfcrit`.
- Tạo báo cáo Word ngắn để bạn chèn số liệu vào bài IEEE.
