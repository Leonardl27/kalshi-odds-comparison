#!/usr/bin/env python3
"""
Very simple script to test different API endpoints for SportsGameOdds.
"""

import requests
import json
import sys

def test_endpoint(api_key, endpoint):
    """Test a specific API endpoint."""
    url = f"https://api.sportsgameodds.com{endpoint}"
    headers = {
        "X-API-Key": api_key
    }
    
    print(f"\n\nTesting endpoint: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        print(f"Status Code: {status_code}")
        
        if status_code == 200:
            data = response.json()
            # Save the response to a file
            filename = f"response_{endpoint.replace('/', '_')}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Response saved to {filename}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return False

def main():
    # Get API key
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your SportsGameOdds API key: ")
    
    # List of endpoints to test
    endpoints = [
        "/v2/sports",
        "/v2/competitions",
        "/v2/sports/SOCCER/events",
        "/v2/sports/SOCCER/competitions",
        "/v2/sports/BASKETBALL/events",
        "/v2/events"
    ]
    
    # Test each endpoint
    success_endpoints = []
    for endpoint in endpoints:
        success = test_endpoint(api_key, endpoint)
        if success:
            success_endpoints.append(endpoint)
    
    # Summary
    print("\n\n=== Summary ===")
    print(f"Tested {len(endpoints)} endpoints")
    print(f"Successful endpoints: {len(success_endpoints)}")
    for endpoint in success_endpoints:
        print(f"  - {endpoint}")

if __name__ == "__main__":
    main()