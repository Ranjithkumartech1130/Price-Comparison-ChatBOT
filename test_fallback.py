import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

class AIModelTemp:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        self.models = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite', 
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-flash-latest',
        ]

    def generate_response(self, prompt, context=None):
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\nUser: {prompt}"

        errors = []
        for model_name in self.models:
            try:
                print(f"Trying {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                return f"Success with {model_name}: {response.text}"
            except Exception as e:
                print(f"Failed {model_name}: {e}")
                time.sleep(1)
        return "All failed"

agent = AIModelTemp()
print(agent.generate_response("Hi"))
