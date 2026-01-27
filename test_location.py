"""
Test script for location-based store finder functionality.
"""
import sys
sys.path.insert(0, 's:/Price Comparison Chatbot')

from backend.location_service import (
    calculate_distance,
    find_nearby_stores,
    generate_mock_stores,
    calculate_destination_point
)

def test_distance_calculation():
    """Test Haversine distance calculation."""
    print("Testing distance calculation...")
    
    # San Francisco to Los Angeles (approx 559 km)
    sf_lat, sf_lon = 37.7749, -122.4194
    la_lat, la_lon = 34.0522, -118.2437
    
    distance = calculate_distance(sf_lat, sf_lon, la_lat, la_lon)
    print(f"  Distance SF to LA: {distance:.2f} km")
    assert 550 < distance < 570, "Distance calculation error"
    print("  [OK] Distance calculation works correctly\n")


def test_destination_point():
    """Test destination point calculation."""
    print("Testing destination point calculation...")
    
    # Start from a point and go 10km north
    start_lat, start_lon = 40.7128, -74.0060  # New York
    distance_km = 10
    bearing = 0  # North
    
    dest_lat, dest_lon = calculate_destination_point(start_lat, start_lon, distance_km, bearing)
    
    # Verify the distance is approximately 10km
    actual_distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
    print(f"  Expected: 10 km, Actual: {actual_distance:.2f} km")
    assert 9.9 < actual_distance < 10.1, "Destination point calculation error"
    print("  [OK] Destination point calculation works correctly\n")


def test_mock_store_generation():
    """Test mock store generation."""
    print("Testing mock store generation...")
    
    user_lat, user_lon = 37.7749, -122.4194  # San Francisco
    product_query = "Sony WH-1000XM5 headphones"
    
    stores = generate_mock_stores(user_lat, user_lon, product_query, 0, 25)
    
    print(f"  Generated {len(stores)} stores")
    assert len(stores) > 0, "No stores generated"
    
    # Check first store structure
    store = stores[0]
    required_fields = ['name', 'address', 'distance', 'latitude', 'longitude', 
                       'rating', 'has_product', 'stock_level', 'price']
    
    for field in required_fields:
        assert field in store, f"Missing field: {field}"
    
    print(f"  Sample store: {store['name']}")
    print(f"    Address: {store['address']}")
    print(f"    Distance: {store['distance']} km")
    print(f"    Rating: {store['rating']}/5.0")
    print(f"    Stock: {store['stock_level']}")
    print(f"    Price: {store['price']}")
    print("  [OK] Mock store generation works correctly\n")


def test_nearby_stores_search():
    """Test the main nearby stores search function."""
    print("Testing nearby stores search...")
    
    user_lat, user_lon = 37.7749, -122.4194  # San Francisco
    product_query = "laptop"
    
    # Test without Google API key (uses mock data)
    stores = find_nearby_stores(
        user_lat=user_lat,
        user_lon=user_lon,
        product_query=product_query,
        min_distance=0,
        max_distance=25,
        google_api_key=None
    )
    
    print(f"  Found {len(stores)} stores within 0-25km")
    assert len(stores) > 0, "No stores found"
    
    # Verify all stores are within the distance range
    for store in stores:
        assert 0 <= store['distance'] <= 25, f"Store distance {store['distance']} out of range"
    
    # Verify stores are sorted by distance
    distances = [s['distance'] for s in stores]
    assert distances == sorted(distances), "Stores not sorted by distance"
    
    print(f"  Closest store: {stores[0]['name']} ({stores[0]['distance']} km)")
    print(f"  Farthest store: {stores[-1]['name']} ({stores[-1]['distance']} km)")
    print("  [OK] Nearby stores search works correctly\n")


def test_distance_filtering():
    """Test distance range filtering."""
    print("Testing distance range filtering...")
    
    user_lat, user_lon = 37.7749, -122.4194
    product_query = "phone"
    
    # Test with custom range (10-15 km)
    stores = find_nearby_stores(
        user_lat=user_lat,
        user_lon=user_lon,
        product_query=product_query,
        min_distance=10,
        max_distance=15,
        google_api_key=None
    )
    
    print(f"  Found {len(stores)} stores within 10-15km")
    
    # Verify all stores are within the specified range
    for store in stores:
        assert 10 <= store['distance'] <= 15, \
            f"Store distance {store['distance']} not in range 10-15km"
    
    print("  [OK] Distance filtering works correctly\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Location Service Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_distance_calculation()
        test_destination_point()
        test_mock_store_generation()
        test_nearby_stores_search()
        test_distance_filtering()
        
        print("=" * 60)
        print("[SUCCESS] All tests passed successfully!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n[FAILED] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
