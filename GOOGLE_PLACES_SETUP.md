# How to Get Google Places API Key for Real Store Locations

## Why You Need This
To show **real stores** with **actual locations** near users (instead of mock/demo data), you need a Google Places API key.

## Step-by-Step Guide

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Create a New Project (or select existing)
- Click "Select a project" at the top
- Click "NEW PROJECT"
- Name it (e.g., "Price Comparison Chatbot")
- Click "CREATE"

### 3. Enable Required APIs
- Go to "APIs & Services" → "Library"
- Search for and enable these APIs:
  - **Places API (New)** ✅
  - **Places API** ✅
  - **Maps JavaScript API** (optional, for map features)

### 4. Create API Credentials
- Go to "APIs & Services" → "Credentials"
- Click "+ CREATE CREDENTIALS"
- Select "API key"
- Copy the generated API key

### 5. Secure Your API Key (Important!)
- Click "Edit API key" (pencil icon)
- Under "API restrictions":
  - Select "Restrict key"
  - Check: Places API, Places API (New)
- Under "Application restrictions":
  - For development: Select "None"
  - For production: Select "HTTP referrers" and add your domain
- Click "SAVE"

### 6. Add to Your Project
Edit your `.env` file:
```bash
GOOGLE_PLACES_API_KEY=AIza...your_actual_key_here
```

### 7. Restart Your Server
```bash
# Stop the current server (Ctrl+C)
# Start it again
python -m uvicorn backend.main:app --reload
```

## Testing

1. Open your app in browser
2. Click "Nearby Stores"
3. Allow location access
4. Search for a product (e.g., "laptop")
5. You should see **real stores** from Google Maps!

## Pricing

Google Places API has a **free tier**:
- **$200 free credit per month**
- Places Nearby Search: $32 per 1000 requests
- Place Details: $17 per 1000 requests

**Example**: With free credit, you get ~6,000 nearby searches/month FREE!

## Without API Key

If you don't add the API key, the app will use **mock data** (demo stores) which still works great for testing and demonstration!

## Troubleshooting

### "API key not valid"
- Make sure you enabled Places API in Google Cloud Console
- Check that you copied the full key
- Wait 1-2 minutes after creating the key

### "This API project is not authorized"
- Enable "Places API" and "Places API (New)" in your project
- Make sure billing is enabled (free tier is fine)

### "ZERO_RESULTS"
- Try a broader search term
- Increase the search radius
- Check if you're in a remote area

### Still seeing mock data?
- Verify the API key is in `.env` file
- Restart the backend server
- Check server logs for errors

## Security Best Practices

✅ **DO**:
- Restrict API key to specific APIs
- Use environment variables (`.env`)
- Add `.env` to `.gitignore`
- Monitor usage in Google Cloud Console

❌ **DON'T**:
- Commit API keys to GitHub
- Share your API key publicly
- Use the same key for multiple projects
- Leave API key unrestricted

## Need Help?

- Google Places API Docs: https://developers.google.com/maps/documentation/places/web-service
- Pricing Calculator: https://mapsplatform.google.com/pricing/
- Support: https://developers.google.com/maps/support
