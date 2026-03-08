import requests
import json
import re
from backend.config import Config

def generate_quiz_from_text(text, num_questions, difficulty, quiz_type):
    diff_desc = {
        "easy": "simple, beginner-friendly questions",
        "medium": "moderately challenging questions",
        "hard": "complex, analytical questions requiring deep understanding"
    }

    if quiz_type == "mcq":
        format_instruction = """Return ONLY valid JSON:
{
  "quiz": [
    {
      "type": "mcq",
      "question": "Question text?",
      "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
      "correct": "A",
      "explanation": "Why this is correct"
    }
  ]
}"""
    else:  # fill in the blanks
        format_instruction = """Return ONLY valid JSON:
{
  "quiz": [
    {
      "type": "fill",
      "question": "The capital of France is ___.",
      "correct": "Paris",
      "explanation": "Paris is the capital city of France"
    }
  ]
}"""

    prompt = f"""You are a quiz generator. Based on the text below, generate exactly {num_questions} {quiz_type} questions at {difficulty} difficulty ({diff_desc[difficulty]}).

TEXT:
{text[:4000]}

INSTRUCTIONS:
- Generate exactly {num_questions} questions
- Difficulty: {difficulty}
- Quiz type: {quiz_type}
- For fill-in-the-blank: use ___ as blank, answer should be 1-3 words
- No markdown, no extra text

{format_instruction}"""

    headers = {
        "Authorization": f"Bearer {Config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": Config.GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 3000
    }

    response = requests.post(Config.GROQ_API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code != 200:
        err = response.json().get("error", {}).get("message", "Unknown API error")
        raise Exception(f"Groq API Error: {err}")

    content = response.json()["choices"][0]["message"]["content"].strip()
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if not match:
        raise Exception("Could not parse quiz JSON from response")

    return json.loads(match.group())
