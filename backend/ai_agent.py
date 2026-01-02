import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

class AIModel:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        # List of models to try in order of preference
        self.models = [
            'gemini-2.0-flash',
            'gemini-2.0-flash-lite', 
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-flash-latest',
            'gemini-1.5-flash-latest',
            'gemini-1.5-flash'
        ]

    def generate_response(self, prompt, context=None):
        if not self.api_key:
            return "Please provide a valid API Key to use the AI features."
            
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\nUser: {prompt}"

        errors = []
        for model_name in self.models:
            try:
                # print(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str:
                    print(f"Model {model_name} quota exceeded. Switching...")
                    errors.append(f"{model_name}: Quota Exceeded")
                    time.sleep(1) # Short cool-down before next model
                    continue
                elif "404" in error_str or "not found" in error_str:
                     print(f"Model {model_name} not found. Switching...")
                     errors.append(f"{model_name}: Not Found")
                     continue
                else:
                    # For other errors, might not want to retry indefinitely, but let's try next model just in case
                    print(f"Model {model_name} error: {e}")
                    errors.append(f"{model_name}: {e}")
                    continue
        
        return "I'm currently receiving a high volume of requests (Google API Quota Exceeded), so I cannot provide a live AI answer right now. However, I can still help you compare prices if you switch to the **Price Comparison** tab!"
