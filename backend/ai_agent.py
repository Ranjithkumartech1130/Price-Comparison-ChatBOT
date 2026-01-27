from google import genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

# List of models to try in order of preference
AVAILABLE_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite', 
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-flash-latest',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash'
]

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModel:
    def __init__(self, api_key: str = None):
        """
        Initialize the AI Model agent.
        
        Args:
            api_key (str, optional): The Google Gemini API key. Defaults to None.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        
        self.models = AVAILABLE_MODELS
        self.disabled_models = {} # model_name -> timestamp of last 429

    def generate_response(self, prompt: str, context: str = None) -> str:
        """
        Generate a response using the available Gemini models.
        
        Args:
            prompt (str): The user's prompt.
            context (str, optional): Additional context for the conversation.
            
        Returns:
            str: The generated response or error message.
        """
        if not self.client:
            return "Please provide a valid API Key to use the AI features."
            
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\nUser: {prompt}"

        now = time.time()
        errors = []
        for model_name in self.models:
            # Skip models on cooldown (60 seconds)
            if model_name in self.disabled_models:
                if now - self.disabled_models[model_name] < 60:
                    continue
                else:
                    del self.disabled_models[model_name]

            try:
                # logger.info(f"Trying model: {model_name}")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota exceeded" in error_str:
                    logger.warning(f"Model {model_name} quota exceeded. Cooling down...")
                    self.disabled_models[model_name] = time.time()
                    errors.append(f"{model_name}: Quota Exceeded")
                    continue
                elif "404" in error_str or "not found" in error_str:
                     logger.warning(f"Model {model_name} not found. Switching...")
                     errors.append(f"{model_name}: Not Found")
                     continue
                else:
                    # For other errors, might not want to retry indefinitely, but let's try next model just in case
                    logger.error(f"Model {model_name} error: {e}")
                    errors.append(f"{model_name}: {e}")
                    continue
        
        return "I'm currently receiving a high volume of requests (Google API Quota Exceeded), so I cannot provide a live AI answer right now. However, I can still help you compare prices if you switch to the **Price Comparison** tab!"
