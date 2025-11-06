"""
Unified API Runner for Hallucination Detection Research
Supports: OpenAI, DeepSeek, Gemini, Ollama
"""

import os
import pandas as pd
import requests
import json
from typing import List, Dict, Optional
from openai import OpenAI
import google.generativeai as genai

# Default prompts
DEFAULT_DIRECT_PROMPT = (
    "Bạn là trợ lý chính xác về sự kiện. Trả lời ngắn gọn một đoạn. "
    "Nếu không chắc chắn, hãy nói 'không chắc'.\n"
    "Câu hỏi: {q}"
)

DEFAULT_SELFCRIT_PROMPT = (
    "Nhiệm vụ: Trả lời rồi tự kiểm tra tính chính xác và sửa lại nếu cần.\n"
    "Bước 1 — Nháp: trả lời ngắn.\n"
    "Bước 2 — Tự kiểm: liệt kê điểm có thể sai hoặc thiếu.\n"
    "Bước 3 — Cuối cùng: đưa đáp án cuối cùng. Nếu không chắc, hãy nói rõ không chắc.\n"
    "Câu hỏi: {q}"
)

class APIRunner:
    """Unified API runner for all LLM providers"""
    
    def __init__(self, provider: str, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = int(os.getenv("TIMEOUT_S", "120"))
        
        self._setup_client()
    
    def _setup_client(self):
        """Setup API client based on provider"""
        if self.provider == "openai":
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "deepseek":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.deepseek.com/v1"
            )
        elif self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        elif self.provider == "ollama":
            self.base_url = self.base_url or "http://localhost:11434"
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def chat_once(self, messages: List[Dict[str, str]]) -> str:
        """Send single chat request to API"""
        try:
            if self.provider in ["openai", "deepseek"]:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    timeout=self.timeout
                )
                return (resp.choices[0].message.content or "").strip()
            
            elif self.provider == "gemini":
                # Convert messages to Gemini format
                prompt = messages[-1]["content"] if messages else ""
                resp = self.client.generate_content(prompt)
                return resp.text.strip() if resp.text else ""
            
            elif self.provider == "ollama":
                # Ollama HTTP API
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
                resp = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout
                )
                resp.raise_for_status()
                return resp.json().get("message", {}).get("content", "").strip()
            
        except Exception as e:
            print(f"API Error: {e}")
            return f"[ERROR: {str(e)}]"
    
    def extract_final_answer(self, text: str) -> str:
        """Extract final answer from self-critique response"""
        if not text:
            return ""
        lowered = text.lower()
        markers = ["cuối cùng", "final", "đáp án cuối", "kết luận"]
        pos = -1
        for m in markers:
            p = lowered.rfind(m)
            if p > pos:
                pos = p
        if pos != -1:
            return text[pos:]
        return text
    
    def run_direct_prompt(self, question: str) -> str:
        """Run direct prompt for a single question"""
        prompt = DEFAULT_DIRECT_PROMPT.format(q=question)
        messages = [{"role": "user", "content": prompt}]
        return self.chat_once(messages)
    
    def run_self_critique_prompt(self, question: str) -> str:
        """Run self-critique prompt for a single question"""
        prompt = DEFAULT_SELFCRIT_PROMPT.format(q=question)
        messages = [{"role": "user", "content": prompt}]
        return self.chat_once(messages)
    
    def extract_final(self, text: str) -> str:
        """Extract final answer from self-critique response"""
        if not text:
            return ""
        lowered = text.lower()
        markers = ["cuối cùng", "final", "đáp án cuối", "kết luận"]
        pos = -1
        for m in markers:
            p = lowered.rfind(m)
            if p > pos:
                pos = p
        if pos != -1:
            return text[pos:]
        return text
    
    def run_experiment(self, input_csv: str, output_csv: str, prompts: Dict[str, str]) -> None:
        """Run complete experiment with direct and self-critique prompts"""
        df = pd.read_csv(input_csv)
        rows = []
        
        direct_template = prompts.get("direct", DEFAULT_DIRECT_PROMPT)
        selfcrit_template = prompts.get("selfcrit", DEFAULT_SELFCRIT_PROMPT)
        
        for i, row in df.iterrows():
            question = row["question"]
            
            # Direct prompt
            direct_prompt = direct_template.format(q=question)
            direct_answer = self.chat_once([{"role": "user", "content": direct_prompt}])
            
            # Self-critique prompt
            selfcrit_prompt = selfcrit_template.format(q=question)
            selfcrit_answer = self.chat_once([{"role": "user", "content": selfcrit_prompt}])
            selfcrit_final = self.extract_final(selfcrit_answer)
            
            rows.append({
                "idx": i + 1,
                "question": question,
                "direct_answer": direct_answer,
                "selfcrit_answer": selfcrit_answer,
                "selfcrit_final_span": selfcrit_final,
                "provider": self.provider,
                "model": self.model,
                "direct_prompt": direct_prompt,
                "selfcrit_prompt": selfcrit_prompt
            })
            
            print(f"[{i+1:02d}] Completed - {self.provider}/{self.model}")
        
        # Save results
        pd.DataFrame(rows).to_csv(output_csv, index=False, encoding="utf-8")
        print(f"Results saved to: {output_csv}")

# Default prompt templates
def main():
    """Main execution function"""
    # Get configuration from environment variables
    provider = os.getenv("API_PROVIDER", "openai").lower()
    model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    input_csv = os.getenv("INPUT_CSV", "data/scientific_facts_basic.csv")
    output_csv = os.getenv("OUT_CSV", f"data/results/{provider}/results_raw.csv")
    
    # Get API credentials
    api_key = None
    base_url = None
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
    elif provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = "https://api.deepseek.com/v1"
    elif provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Validate credentials
    if provider != "ollama" and not api_key:
        raise RuntimeError(f"Missing API key for {provider}. Set environment variable.")
    
    # Create output directory
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    # Run experiment
    runner = APIRunner(provider, model, api_key, base_url)
    prompts = {
        "direct": DEFAULT_DIRECT_PROMPT,
        "selfcrit": DEFAULT_SELFCRIT_PROMPT
    }
    
    runner.run_experiment(input_csv, output_csv, prompts)

if __name__ == "__main__":
    main()