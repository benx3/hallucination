# openai_run.py# openai_run.py

# REQUIRE: pip install openai pandas python-dotenv# REQUIRE: pip install openai pandas python-dotenv

import os

import osimport pandas as pd

import pandas as pdfrom typing import List, Dict

from typing import List, Dictfrom openai import OpenAI

from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")INPUT_CSV    = os.getenv("INPUT_CSV", "questions_50_hard.csv")

INPUT_CSV    = os.getenv("INPUT_CSV", "questions_50_hard.csv")OUT_CSV      = os.getenv("OUT_CSV", "openai2/results_raw_openai.csv")

OUT_CSV      = os.getenv("OUT_CSV", "openai2/results_raw_openai.csv")TIMEOUT_S    = int(os.getenv("TIMEOUT_S", "120"))

TIMEOUT_S    = int(os.getenv("TIMEOUT_S", "120"))

DIRECT_TMPL = (

DIRECT_TMPL = (    "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn. "

    "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn. "    "Nếu không chắc chắn, hãy nói 'không chắc'.\n"

    "Nếu không chắc chắn, hãy nói 'không chắc'.\n"    "Câu hỏi: {q}"

    "Câu hỏi: {q}")

)

SELFCRIT_TMPL = (

SELFCRIT_TMPL = (    "Nhiệm vụ: Trả lời rồi tự kiểm tra tính chính xác và sửa lại nếu cần.\n"

    "Nhiệm vụ: Trả lời rồi tự kiểm tra tính chính xác và sửa lại nếu cần.\n"    "Bước 1 — Nháp: trả lời ngắn.\n"

    "Bước 1 — Nháp: trả lời ngắn.\n"    "Bước 2 — Tự kiểm: liệt kê điểm có thể sai hoặc thiếu.\n"

    "Bước 2 — Tự kiểm: liệt kê điểm có thể sai hoặc thiếu.\n"    "Bước 3 — Cuối cùng: đưa đáp án cuối cùng. Nếu không chắc, hãy nói rõ không chắc.\n"

    "Bước 3 — Cuối cùng: đưa đáp án cuối cùng. Nếu không chắc, hãy nói rõ không chắc.\n"    "Câu hỏi: {q}"

    "Câu hỏi: {q}")

)

def chat_once(client: OpenAI, messages: List[Dict[str, str]]) -> str:

def chat_once(client: OpenAI, messages: List[Dict[str, str]]) -> str:    resp = client.chat.completions.create(

    """Send single chat request to OpenAI API"""        model=OPENAI_MODEL,

    resp = client.chat.completions.create(        messages=messages,

        model=OPENAI_MODEL,        timeout=TIMEOUT_S

        messages=messages,    )

        timeout=TIMEOUT_S    return (resp.choices[0].message.content or "").strip()

    )

    return (resp.choices[0].message.content or "").strip()def extract_final(text: str) -> str:

    if not text:

def extract_final(text: str) -> str:        return ""

    """Extract final answer from self-critique response"""    lowered = text.lower()

    if not text:    markers = ["cuối cùng", "final", "đáp án cuối"]

        return ""    pos = -1

    lowered = text.lower()    for m in markers:

    markers = ["cuối cùng", "final", "đáp án cuối"]        p = lowered.rfind(m)

    pos = -1        if p > pos:

    for m in markers:            pos = p

        p = lowered.rfind(m)    if pos != -1:

        if p > pos:        return text[pos:]

            pos = p    return text

    if pos != -1:

        return text[pos:]def main():

    return text    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:

def main():        raise RuntimeError("Thiếu OPENAI_API_KEY trong biến môi trường.")

    # Get API key from environment variables only    client = OpenAI(api_key=api_key)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:    df = pd.read_csv(INPUT_CSV)

        raise RuntimeError("Missing OPENAI_API_KEY environment variable. Please set it before running.")    rows = []

        for i, row in df.iterrows():

    client = OpenAI(api_key=api_key)        q = row["question"]



    # Load questions        d_prompt = DIRECT_TMPL.format(q=q)

    df = pd.read_csv(INPUT_CSV)        d_ans = chat_once(client, [{"role":"user","content": d_prompt}])

    rows = []

            s_prompt = SELFCRIT_TMPL.format(q=q)

    for i, row in df.iterrows():        s_ans = chat_once(client, [{"role":"user","content": s_prompt}])

        q = row["question"]        s_final = extract_final(s_ans)

        print(f"[{i+1:02d}] Processing: {q[:50]}...")

        rows.append({

        # Direct prompting            "idx": i+1,

        d_prompt = DIRECT_TMPL.format(q=q)            "question": q,

        d_ans = chat_once(client, [{"role":"user","content": d_prompt}])            "direct_answer": d_ans,

            "selfcrit_answer": s_ans,

        # Self-critique prompting            "selfcrit_final_span": s_final

        s_prompt = SELFCRIT_TMPL.format(q=q)        })

        s_ans = chat_once(client, [{"role":"user","content": s_prompt}])        print(f"[{i+1:02d}] xong")

        s_final = extract_final(s_ans)

    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")

        rows.append({    print(f"Đã ghi {OUT_CSV}")

            "idx": i+1,

            "question": q,if __name__ == "__main__":

            "direct_answer": d_ans,    main()
            "selfcrit_answer": s_ans,
            "selfcrit_final_span": s_final
        })
        print(f"[{i+1:02d}] ✓ Done")

    # Save results
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Results saved to {OUT_CSV}")

if __name__ == "__main__":
    main()