# run_ollama_eval.py
# REQUIRE: pip install requests pandas python-dotenv
import os, requests
import pandas as pd
from typing import Dict, List

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME  = os.getenv("MODEL_NAME", "llama3.2")
TIMEOUT_S   = int(os.getenv("TIMEOUT_S", "120"))
INPUT_CSV   = os.getenv("INPUT_CSV", "questions_50_hard.csv")
OUT_CSV     = os.getenv("OUT_CSV", "ollama2/results_raw.csv")

DIRECT_TMPL = (
    "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn."
    " Nếu không chắc chắn, hãy nói 'không chắc'.\n"
    "Câu hỏi: {q}"
)

SELFCRIT_TMPL = (
    "Nhiệm vụ: Trả lời rồi tự kiểm tra tính chính xác và sửa lại nếu cần.\n"
    "Bước 1 — Nháp: trả lời ngắn.\n"
    "Bước 2 — Tự kiểm: liệt kê điểm có thể sai hoặc thiếu.\n"
    "Bước 3 — Cuối cùng: đưa đáp án cuối cùng. Nếu không chắc, hãy nói rõ không chắc.\n"
    "Câu hỏi: {q}"
)

def ollama_chat(messages: List[Dict]) -> str:
    url = f"{OLLAMA_HOST}/api/chat"
    payload = {"model": MODEL_NAME, "messages": messages, "stream": False}
    r = requests.post(url, json=payload, timeout=TIMEOUT_S)
    r.raise_for_status()
    data = r.json()
    return (data.get("message", {}) or {}).get("content", "").strip()

def extract_final(text: str) -> str:
    if not text:
        return ""
    lowered = text.lower()
    markers = ["cuối cùng", "final", "đáp án cuối"]
    pos = -1
    for m in markers:
        p = lowered.rfind(m)
        if p > pos:
            pos = p
    if pos != -1:
        return text[pos:]
    return text

def main():
    df = pd.read_csv(INPUT_CSV)
    rows = []
    for i, row in df.iterrows():
        q = row["question"]
        d_prompt = DIRECT_TMPL.format(q=q)
        d_ans = ollama_chat([{"role":"user","content": d_prompt}])

        s_prompt = SELFCRIT_TMPL.format(q=q)
        s_ans = ollama_chat([{"role":"user","content": s_prompt}])
        s_final = extract_final(s_ans)

        rows.append({
            "idx": i+1,
            "question": q,
            "direct_answer": d_ans,
            "selfcrit_answer": s_ans,
            "selfcrit_final_span": s_final
        })
        print(f"[{i+1:02d}] xong")

    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"Đã ghi {OUT_CSV}")

if __name__ == "__main__":
    main()