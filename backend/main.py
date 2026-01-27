import os
import uvicorn
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.scraper import custom_scraper
from backend.ai_agent import AIModel
from backend.location_service import find_nearby_stores

app = FastAPI()

# Input Models
class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    history: Optional[List[dict]] = []

class PriceRequest(BaseModel):
    query: str
    api_key: Optional[str] = None # Optional, if we want AI to summarize
    country_code: Optional[str] = "US"

class LocationRequest(BaseModel):
    query: str
    latitude: float
    longitude: float
    min_distance: Optional[float] = 0
    max_distance: Optional[float] = 25
    api_key: Optional[str] = None
    google_api_key: Optional[str] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify server status."""
    return {"status": "healthy"}

@app.post("/api/chat/general")
async def general_chat(request: ChatRequest):
    """
    Handle general chat requests using the AI agent.
    
    Args:
        request (ChatRequest): The chat request object containing message and history.
        
    Returns:
        dict: The response from the AI agent.
    """
    # API key is now optional in request if set in env
    agent = AIModel(api_key=request.api_key)
    
    # Construct simplistic history string
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in request.history[-5:]])
    response = agent.generate_response(request.message, context=context)
    return {"response": response}

@app.post("/api/chat/price")
async def price_comparison(request: PriceRequest):
    # 1. Scrape Data
    print(f"Scraping for: {request.query} in {request.country_code}")
    data = custom_scraper(request.query, country_code=request.country_code)
    
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

@app.post("/api/chat/nearby-stores")
async def nearby_stores(request: LocationRequest):
    """
    Find nearby stores that have the specified product within the distance range.
    
    Args:
        request (LocationRequest): Contains query, location, and distance preferences
        
    Returns:
        dict: List of nearby stores with product availability and AI recommendations
    """
    print(f"Searching for '{request.query}' near ({request.latitude}, {request.longitude})")
    print(f"Distance range: {request.min_distance}km - {request.max_distance}km")
    
    # Get Google API key from environment or request
    google_api_key = request.google_api_key or os.getenv("GOOGLE_PLACES_API_KEY")
    
    # Find nearby stores
    stores = find_nearby_stores(
        user_lat=request.latitude,
        user_lon=request.longitude,
        product_query=request.query,
        min_distance=request.min_distance,
        max_distance=request.max_distance,
        google_api_key=google_api_key
    )
    
    if not stores:
        return {
            "response": f"No stores found within {request.min_distance}-{request.max_distance}km that carry '{request.query}'. Try expanding your search radius.",
            "data": [],
            "total_stores": 0
        }
    
    # Filter only stores that have the product
    stores_with_product = [s for s in stores if s.get('has_product', False)]
    
    # Generate AI summary
    ai_summary = ""
    try:
        agent = AIModel(api_key=request.api_key)
        
        # Create a concise summary of stores for AI
        store_summary = "\n".join([
            f"- {s['name']} ({s['distance']}km away): {s.get('stock_level', 'Available')}, Rating: {s.get('rating', 'N/A')}/5"
            for s in stores_with_product[:5]
        ])
        
        prompt = f"""Based on these nearby stores selling '{request.query}':
{store_summary}

Provide a brief, friendly recommendation (2-3 sentences) on which store(s) to visit first, considering distance, ratings, and stock availability. Be conversational and helpful."""
        
        ai_summary = agent.generate_response(prompt)
    except Exception as e:
        print(f"AI Summary failed: {e}")
        ai_summary = f"Found {len(stores_with_product)} nearby stores carrying '{request.query}'. Check the list below for details!"
    
    return {
        "response": ai_summary,
        "data": stores_with_product,
        "total_stores": len(stores_with_product),
        "search_radius": f"{request.min_distance}-{request.max_distance}km"
    }


# Serve Frontend
# We assume frontend files will be in 'frontend' folder in the root
# Checking if directory exists first to avoid errors during initial setup
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
