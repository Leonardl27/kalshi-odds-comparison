#!/usr/bin/env python3
"""
Script to inspect the exact structure of the SportsGameOdds API response.
"""

import requests
import json
import pprint

def inspect_api_response(api_key):
    """Get and inspect the structure of the API response."""
    url = "https://api.sportsgameodds.com/v2/sports/"
    headers = {
        "X-API-Key": api_key
    }
    
    print(f"Connecting to {url} with API key: {api_key}")
    
    try:
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        print(f"Status Code: {status_code}")
        
        if status_code == 200:
            # Get the raw response
            data = response.json()
            
            # Save the response to a file
            with open("api_raw_response.json", "w") as f:
                json.dump(data, f, indent=2)
            print("\nFull response saved to api_raw_response.json")
            
            # Print the type and structure
            print(f"\nResponse Type: {type(data)}")
            print("\nResponse Structure:")
            pprint.pprint(data, depth=2)
            
            # If it's a dictionary, print the keys
            if isinstance(data, dict):
                print("\nTop-level keys:", list(data.keys()))
                
                # Check if 'data' key exists
                if 'data' in data:
                    print("\nData key type:", type(data['data']))
                    if isinstance(data['data'], list):
                        print(f"Number of items in data list: {len(data['data'])}")
                        if data['data']:
                            print("\nFirst item in data list:")
                            pprint.pprint(data['data'][0])
            
            # If it's a list, print the length and first item
            elif isinstance(data, list):
                print(f"\nNumber of items in list: {len(data)}")
                if data:
                    print("\nFirst item:")
                    pprint.pprint(data[0])
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    # Your SportsGameOdds API key
    api_key = "bf9f835f4831b0f04e32e612dd07250b"
    
    inspect_api_response(api_key)