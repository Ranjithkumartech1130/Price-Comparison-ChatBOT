# Location-Based Store Finder Feature

## Overview
The Price Comparison Chatbot now includes a **Nearby Stores** feature that helps users find physical stores within their area (10-25km radius) that carry the products they're searching for.

## Features

### 🗺️ Location Access
- **Browser Geolocation API**: Requests user's location with their permission
- **Privacy-Focused**: Location is only used for the current search and is not stored
- **Error Handling**: Comprehensive error messages for permission denied, unavailable location, or timeout scenarios

### 📍 Distance Control
- **Customizable Range**: Users can set minimum (0-20km) and maximum (5-50km) search distances
- **Interactive Sliders**: Real-time distance range adjustment with visual feedback
- **Smart Defaults**: Default range of 0-25km for optimal results

### 🏪 Store Information
Each nearby store displays:
- **Store Name & Location**: Full store name with address
- **Distance**: Precise distance in kilometers from user's location
- **Ratings**: Star ratings and total number of reviews
- **Stock Status**: Real-time product availability (In Stock, Low Stock, Limited Stock, Call to Verify)
- **Open/Closed Status**: Current operating status
- **Price**: Product price at that location
- **Contact Info**: Phone number and website (when available)

### 🎯 Smart Actions
- **View on Map**: Direct link to Google Maps with store coordinates
- **Call Store**: One-click phone dialing (on mobile devices)
- **Visit Website**: Quick access to store's online presence

## How to Use

### Step 1: Enable Location Access
1. Click on the **"Nearby Stores"** button in the sidebar
2. Click **"Allow Location Access"** when prompted
3. Grant location permission in your browser

### Step 2: Set Distance Range
1. Adjust the **Minimum Distance** slider (0-20km)
2. Adjust the **Maximum Distance** slider (5-50km)
3. The range ensures you only see stores within your preferred travel distance

### Step 3: Search for Products
1. Type the product name in the search box (e.g., "Sony WH-1000XM5 headphones")
2. Press Enter or click Send
3. View nearby stores that have the product in stock

## Technical Implementation

### Backend (`location_service.py`)
- **Haversine Formula**: Accurate distance calculations between coordinates
- **Google Places API Integration**: Real store data (when API key is provided)
- **Mock Data Generation**: Realistic demo stores for testing without API key
- **Distance Filtering**: Efficient filtering within specified range
- **Product Matching**: Filters stores based on product availability

### Frontend
- **Geolocation API**: Browser-native location access
- **Distance Sliders**: Interactive range controls
- **Store Cards**: Beautiful, responsive store display
- **Map Integration**: Google Maps links for navigation
- **Error Handling**: User-friendly error messages

### API Endpoint
```
POST /api/chat/nearby-stores
```

**Request Body:**
```json
{
  "query": "product name",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "min_distance": 0,
  "max_distance": 25,
  "api_key": "optional_gemini_api_key",
  "google_api_key": "optional_google_places_api_key"
}
```

**Response:**
```json
{
  "response": "AI-generated recommendation",
  "data": [
    {
      "name": "Best Buy - Store #123",
      "address": "123 Main St",
      "distance": 5.2,
      "latitude": 37.7849,
      "longitude": -122.4094,
      "rating": 4.5,
      "total_ratings": 1234,
      "open_now": true,
      "phone": "+1-555-123-4567",
      "website": "https://www.bestbuy.com",
      "has_product": true,
      "stock_level": "In Stock",
      "price": "$299.99"
    }
  ],
  "total_stores": 8,
  "search_radius": "0-25km"
}
```

## Configuration

### Optional: Google Places API
To use real store data instead of mock data:

1. Get a Google Places API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Add to your `.env` file:
   ```
   GOOGLE_PLACES_API_KEY=your_api_key_here
   ```

### Without Google Places API
The feature works perfectly with generated mock data that simulates realistic stores based on:
- Product category detection
- Random but realistic distances
- Store chain names (Best Buy, Walmart, Target, etc.)
- Realistic ratings, stock levels, and contact information

## Privacy & Security

- ✅ Location is **never stored** on the server
- ✅ Location is **only used** for the current search
- ✅ User must **explicitly grant** permission
- ✅ Works in **HTTPS** environments (required by browsers)
- ✅ No tracking or analytics on location data

## Browser Compatibility

- ✅ Chrome/Edge (v50+)
- ✅ Firefox (v55+)
- ✅ Safari (v11+)
- ✅ Opera (v40+)
- ❌ Internet Explorer (not supported)

## Troubleshooting

### "Location access denied"
- Check browser permissions: Settings → Privacy → Location
- Ensure site is using HTTPS (required for geolocation)
- Try a different browser

### "Location information unavailable"
- Check device location services are enabled
- Ensure GPS/Wi-Fi is active
- Try refreshing the page

### "No stores found"
- Increase the maximum distance range
- Try a more general product search term
- Check if you're in a remote area

## Future Enhancements

- 🔄 Real-time inventory sync with store APIs
- 🚗 Driving directions and estimated travel time
- 💰 Price comparison across nearby stores
- 📅 Store hours and holiday schedules
- 🎫 In-store pickup availability
- 🔔 Notifications for stock updates
- 🗺️ Interactive map view with all stores plotted

## Credits

- **Geolocation**: Browser Geolocation API
- **Maps**: Google Maps API
- **Distance Calculation**: Haversine Formula
- **Store Data**: Google Places API (optional)
