# tutor.py
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

from config import SYSTEM_PROMPT, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

def get_llm_call():
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if groq_key and groq_key.strip():
        from groq import Groq
        client = Groq(api_key=groq_key)

        @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
        def llm_call(prompt: str, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS):
            try:
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Groq Error: {str(e)}"
        return llm_call, "Groq (Llama3-70B)"

    elif gemini_key and gemini_key.strip():
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')

        @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=60))
        def llm_call(prompt: str, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
                )
                return response.text
            except Exception as e:
                return f"Gemini Error: {str(e)}"
        return llm_call, "Gemini (2.5 Flash-Lite)"

    else:
        def llm_call(prompt: str, temperature=0.7, max_tokens=2048):
            return "Error: No API key found in .env (GROQ_API_KEY or GEMINI_API_KEY)"
        return llm_call, "No LLM Configured"


llm_call, current_llm = get_llm_call()