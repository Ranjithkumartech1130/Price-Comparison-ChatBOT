import math
import requests
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two coordinates using the Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def find_nearby_stores(
    user_lat: float,
    user_lon: float,
    product_query: str,
    min_distance: float = 0,
    max_distance: float = 25,
    google_api_key: Optional[str] = None
) -> List[Dict]:
    """
    Find nearby stores that sell the specified product within the distance range.
    
    Args:
        user_lat: User's latitude
        user_lon: User's longitude
        product_query: Product search query
        min_distance: Minimum distance in km (default: 0)
        max_distance: Maximum distance in km (default: 25)
        google_api_key: Google Places API key (optional)
    
    Returns:
        List of stores with product availability, distance, and details
    """
    stores = []
    
    # Always try Google Places API first if key is provided
    if google_api_key:
        try:
            logger.info(f"Searching Google Places for '{product_query}' within {max_distance}km")
            stores = search_google_places(user_lat, user_lon, product_query, max_distance, google_api_key)
            logger.info(f"Found {len(stores)} real stores from Google Places")
        except Exception as e:
            logger.error(f"Error searching Google Places: {e}")
            # Don't fall back to mock data - return empty if API fails
            stores = []
    
    # If no Google API key or no results, use mock data as fallback
    if not stores:
        logger.info(f"Using mock data for '{product_query}'")
        stores = generate_mock_stores(user_lat, user_lon, product_query, min_distance, max_distance)
    
    # Filter by distance range
    filtered_stores = [
        store for store in stores 
        if min_distance <= store['distance'] <= max_distance
    ]
    
    # Sort by distance
    filtered_stores.sort(key=lambda x: x['distance'])
    
    logger.info(f"Returning {len(filtered_stores)} stores within {min_distance}-{max_distance}km")
    return filtered_stores


def search_google_places(
    lat: float,
    lon: float,
    query: str,
    radius_km: float,
    api_key: str
) -> List[Dict]:
    """
    Search for real stores using Google Places API with enhanced product matching.
    """
    radius_meters = int(radius_km * 1000)
    stores = []
    
    # Determine store types based on product query
    store_types = determine_store_types(query)
    
    # Try multiple search strategies for better results
    search_strategies = [
        # Strategy 1: Product + store type
        {"keyword": f"{query}", "type": store_types[0] if store_types else "store"},
        # Strategy 2: Just product name
        {"keyword": query, "type": None},
        # Strategy 3: Generic store type only
        {"keyword": "", "type": store_types[0] if store_types else "electronics_store"}
    ]
    
    for strategy in search_strategies:
        if stores:
            break  # Stop if we found stores
            
        try:
            strategy_stores = perform_places_search(
                lat, lon, radius_meters, api_key, 
                keyword=strategy["keyword"], 
                place_type=strategy["type"]
            )
            if strategy_stores:
                stores.extend(strategy_stores)
                logger.info(f"Found {len(strategy_stores)} stores with strategy: {strategy}")
        except Exception as e:
            logger.warning(f"Search strategy failed: {e}")
            continue
    
    return stores


def determine_store_types(query: str) -> List[str]:
    """Determine appropriate store types based on product query."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["laptop", "phone", "headphone", "camera", "tv", "electronics", "computer"]):
        return ["electronics_store", "store", "shopping_mall"]
    elif any(word in query_lower for word in ["book", "novel", "magazine"]):
        return ["book_store", "store"]
    elif any(word in query_lower for word in ["shirt", "pants", "dress", "clothing", "shoes", "fashion"]):
        return ["clothing_store", "shoe_store", "store"]
    elif any(word in query_lower for word in ["food", "grocery", "snack"]):
        return ["grocery_or_supermarket", "supermarket", "store"]
    else:
        return ["store", "shopping_mall", "department_store"]


def perform_places_search(
    lat: float,
    lon: float,
    radius_meters: int,
    api_key: str,
    keyword: str = "",
    place_type: Optional[str] = None
) -> List[Dict]:
    """Perform a single Google Places API search."""
    
    # Build search parameters
    search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius_meters,
        "key": api_key
    }
    
    # Add keyword if provided
    if keyword:
        params["keyword"] = keyword
    
    # Add type if provided
    if place_type:
        params["type"] = place_type
    
    response = requests.get(search_url, params=params, timeout=10)
    data = response.json()
    
    stores = []
    
    if data.get("status") == "OK":
        for place in data.get("results", [])[:15]:  # Get up to 15 results
            place_lat = place["geometry"]["location"]["lat"]
            place_lon = place["geometry"]["location"]["lng"]
            distance = calculate_distance(lat, lon, place_lat, place_lon)
            
            # Get more details about the place
            details = get_place_details(place["place_id"], api_key)
            
            stores.append({
                "name": place.get("name", "Unknown Store"),
                "address": place.get("vicinity", "Address not available"),
                "distance": round(distance, 2),
                "latitude": place_lat,
                "longitude": place_lon,
                "rating": place.get("rating", 0),
                "total_ratings": place.get("user_ratings_total", 0),
                "open_now": place.get("opening_hours", {}).get("open_now", None),
                "phone": details.get("phone", "N/A"),
                "website": details.get("website", "N/A"),
                "place_id": place["place_id"],
                "has_product": True,  # Assume availability based on search
                "stock_level": "Call to Verify",  # Real stores need verification
                "price": "Call for Price",  # Real stores need price verification
                "is_real_data": True
            })
    elif data.get("status") == "ZERO_RESULTS":
        logger.info(f"No results found for keyword='{keyword}', type='{place_type}'")
    else:
        logger.warning(f"Google Places API returned status: {data.get('status')}")
    
    return stores


def get_place_details(place_id: str, api_key: str) -> Dict:
    """
    Get detailed information about a specific place.
    """
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,opening_hours",
        "key": api_key
    }
    
    try:
        response = requests.get(details_url, params=params, timeout=5)
        data = response.json()
        
        if data.get("status") == "OK":
            result = data.get("result", {})
            return {
                "phone": result.get("formatted_phone_number", "N/A"),
                "website": result.get("website", "N/A")
            }
    except Exception as e:
        logger.error(f"Error getting place details: {e}")
    
    return {"phone": "N/A", "website": "N/A"}


def generate_mock_stores(
    user_lat: float,
    user_lon: float,
    product_query: str,
    min_distance: float,
    max_distance: float
) -> List[Dict]:
    """
    Generate mock store data for demonstration purposes.
    Creates realistic-looking stores at various distances.
    """
    import random
    
    # Common store chains based on product type
    store_chains = {
        "electronics": ["Best Buy", "Walmart", "Target", "Micro Center", "Croma", "Reliance Digital"],
        "general": ["Walmart", "Target", "Costco", "Big Bazaar", "D-Mart", "Spencer's"],
        "books": ["Barnes & Noble", "Books-A-Million", "Crossword", "Landmark"],
        "clothing": ["Macy's", "Nordstrom", "Westside", "Pantaloons", "Lifestyle"]
    }
    
    # Determine store type based on query
    query_lower = product_query.lower()
    if any(word in query_lower for word in ["laptop", "phone", "headphone", "camera", "tv", "electronics"]):
        stores_list = store_chains["electronics"]
    elif any(word in query_lower for word in ["book", "novel", "magazine"]):
        stores_list = store_chains["books"]
    elif any(word in query_lower for word in ["shirt", "pants", "dress", "clothing", "shoes"]):
        stores_list = store_chains["clothing"]
    else:
        stores_list = store_chains["general"]
    
    stores = []
    num_stores = random.randint(5, 12)
    
    for i in range(num_stores):
        # Generate random distance within range
        distance = random.uniform(min_distance, max_distance)
        
        # Generate random bearing (direction)
        bearing = random.uniform(0, 360)
        
        # Calculate store coordinates based on distance and bearing
        store_lat, store_lon = calculate_destination_point(user_lat, user_lon, distance, bearing)
        
        store_name = random.choice(stores_list)
        
        # Generate realistic address
        street_num = random.randint(100, 9999)
        streets = ["Main St", "Market Rd", "Commercial St", "MG Road", "Park Ave", "Broadway", "High St"]
        street = random.choice(streets)
        
        stores.append({
            "name": f"{store_name} (Demo)",
            "address": f"{street_num} {street} (Simulated)",
            "distance": round(distance, 2),
            "latitude": store_lat,
            "longitude": store_lon,
            "rating": round(random.uniform(3.5, 5.0), 1),
            "total_ratings": random.randint(50, 5000),
            "open_now": random.choice([True, False, None]),
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "website": f"https://www.{store_name.lower().replace(' ', '')}.com",
            "has_product": random.random() > 0.2,  # 80% chance of having the product
            "stock_level": random.choice(["In Stock", "Low Stock", "Limited Stock", "Call to Verify"]),
            "price": generate_mock_price(product_query),
            "is_real_data": False
        })
    
    return stores


def calculate_destination_point(lat: float, lon: float, distance_km: float, bearing_degrees: float) -> Tuple[float, float]:
    """
    Calculate destination coordinates given a starting point, distance, and bearing.
    
    Args:
        lat: Starting latitude
        lon: Starting longitude
        distance_km: Distance in kilometers
        bearing_degrees: Bearing in degrees (0-360)
    
    Returns:
        Tuple of (destination_lat, destination_lon)
    """
    R = 6371  # Earth's radius in km
    
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing_degrees)
    
    dest_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance_km / R) +
        math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(bearing_rad)
    )
    
    dest_lon_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_km / R) * math.cos(lat_rad),
        math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(dest_lat_rad)
    )
    
    return math.degrees(dest_lat_rad), math.degrees(dest_lon_rad)


def generate_mock_price(product_query: str) -> str:
    """
    Generate a mock price based on the product query.
    """
    import random
    
    # Estimate price range based on product type
    query_lower = product_query.lower()
    
    if "laptop" in query_lower or "macbook" in query_lower:
        price = random.randint(500, 2500)
    elif "phone" in query_lower or "iphone" in query_lower or "samsung" in query_lower:
        price = random.randint(200, 1500)
    elif "headphone" in query_lower or "earbuds" in query_lower:
        price = random.randint(50, 400)
    elif "tv" in query_lower or "television" in query_lower:
        price = random.randint(300, 2000)
    elif "book" in query_lower:
        price = random.randint(10, 50)
    else:
        price = random.randint(20, 500)
    
    # Add some variance
    price = price + random.randint(-50, 50)
    
    return f"${price}.99"
