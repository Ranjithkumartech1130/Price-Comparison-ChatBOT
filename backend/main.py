from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import os
import uvicorn
from backend.scraper import custom_scraper
from backend.ai_agent import AIModel

app = FastAPI()

# Input Models
class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    history: Optional[List[dict]] = []

class PriceRequest(BaseModel):
    query: str
    api_key: Optional[str] = None # Optional, if we want AI to summarize

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat/general")
async def general_chat(request: ChatRequest):
    # API key is now optional in request if set in env
    agent = AIModel(api_key=request.api_key)
    
    # Construct simplistic history string
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.history[-5:]])
    response = agent.generate_response(request.message, context=context)
    return {"response": response}

@app.post("/api/chat/price")
async def price_comparison(request: PriceRequest):
    # 1. Scrape Data
    print(f"Scraping for: {request.query}")
    data = custom_scraper(request.query)
    
    if not data:
        return {
            "response": "I couldn't find any products matching your search on the supported sites.",
            "data": []
        }
    
    # 2. (Optional) Use AI to summarize
    ai_summary = ""
    # Always try to use AI if model is available (via default or passed key)
    try:
        agent = AIModel(api_key=request.api_key)
        prompt = f"Here is a list of product prices found for '{request.query}': {data}. Please give a very brief recommendation on the best deal. Do not use markdown tables, just text."
        ai_summary = agent.generate_response(prompt)
    except Exception as e:
        print(f"AI Summary failed: {e}")
        ai_summary = "" # Fallback if AI fails or no key


    return {
        "response": ai_summary if ai_summary else "Here are the price comparisons I found:",
        "data": data
    }

# Serve Frontend
# We assume frontend files will be in 'frontend' folder in the root
# Checking if directory exists first to avoid errors during initial setup
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
