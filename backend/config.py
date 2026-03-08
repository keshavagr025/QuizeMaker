import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/quizforge")
    JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
