# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
DEFAULT_TEMPERATURE = 0.6
DEFAULT_MAX_TOKENS = 2048

SYSTEM_PROMPT = (
    "You are an expert, encouraging NPTEL tutor. "
    "Provide clear, exam-focused, in-depth summaries using simple language, "
    "real-life analogies, bullet points, tables, and key exam tips."
)

# Default values
DEFAULT_EXAM_DATE = "2026-04-17"
DEFAULT_DAILY_HOURS = 2.5