import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with open("models_list.txt", "w") as f:
    try:
        for m in genai.list_models():
            f.write(f"Name: {m.name}\n")
            f.write(f"Supported methods: {m.supported_generation_methods}\n")
            f.write("-" * 20 + "\n")
    except Exception as e:
        f.write(f"Error: {e}")
