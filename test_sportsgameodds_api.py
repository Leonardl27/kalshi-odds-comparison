#!/usr/bin/env python3
"""
Updated test script for the SportsGameOdds API.
This script verifies API connectivity and retrieves sample data.
"""

import requests
import json
import sys
import yaml
import os
from datetime import datetime

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def test_api_connection(api_key):
    """Test connection to the SportsGameOdds API."""
    url = "https://api.sportsgameodds.com/v2/sports/"
    headers = {
        "X-API-Key": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        print("\n=== API Connection Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f} seconds")
        
        data = response.json()
        
        # Check if the response has the expected structure
        if 'data' in data and isinstance(data['data'], list):
            sports = data['data']
            print(f"Available Sports: {len(sports)}")
            
            # Display first few sports as a sample
            print("\nSample Sports:")
            for i, sport in enumerate(sports[:5], 1):
                print(f"  {i}. {sport.get('name', 'N/A')} (ID: {sport.get('sportID', 'N/A')})")
            
            return True, sports
        else:
            print("\n❌ Unexpected API response structure")
            print(f"Response: {data}")
            return False, None
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error connecting to API: {str(e)}")
        return False, None

def get_soccer_matches(api_key):
    """Get upcoming soccer matches."""
    url = "https://api.sportsgameodds.com/v2/events"
    headers = {
        "X-API-Key": api_key
    }
    params = {
        "sportId": "SOCCER",  # Using sport ID instead of name
        "status": "UPCOMING",
        "includeMarkets": "true"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if the response has the expected structure
        if 'data' in data and isinstance(data['data'], list):
            matches = data['data']
            
            print("\n=== Soccer Matches ===")
            print(f"Total Matches: {len(matches)}")
            
            # Display a few matches as samples
            print("\nSample Matches:")
            for i, match in enumerate(matches[:3], 1):
                home_team = match.get('homeTeam', {}).get('name', 'Unknown')
                away_team = match.get('awayTeam', {}).get('name', 'Unknown')
                start_time = match.get('startTime', 'Unknown')
                
                print(f"  {i}. {home_team} vs {away_team} - {start_time}")
                
                # Show available markets if any
                markets = match.get('markets', [])
                if markets:
                    print(f"     Markets available: {len(markets)}")
                    # Show details of the first market as an example
                    if len(markets) > 0:
                        market = markets[0]
                        print(f"     Sample Market: {market.get('name', 'N/A')}")
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes[:2]:  # Show first 2 outcomes
                            name = outcome.get('name', 'N/A')
                            price = outcome.get('price', 'N/A')
                            print(f"       - {name}: {price}")
                else:
                    print("     No markets available")
            
            return True, matches
        else:
            print("\n❌ Unexpected API response structure for soccer matches")
            print(f"Response: {data}")
            return False, None
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching soccer matches: {str(e)}")
        return False, None

def get_spread_markets(api_key):
    """Get spread markets for soccer matches."""
    url = "https://api.sportsgameodds.com/v2/markets"
    headers = {
        "X-API-Key": api_key
    }
    params = {
        "sportId": "SOCCER",
        "marketType": "SPREAD",
        "status": "UPCOMING"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if the response has the expected structure
        if 'data' in data and isinstance(data['data'], list):
            markets = data['data']
            
            print("\n=== Soccer Spread Markets ===")
            print(f"Total Spread Markets: {len(markets)}")
            
            # Display a few markets as samples
            print("\nSample Spread Markets:")
            for i, market in enumerate(markets[:3], 1):
                event = market.get('event', {})
                home_team = event.get('homeTeam', {}).get('name', 'Unknown')
                away_team = event.get('awayTeam', {}).get('name', 'Unknown')
                market_name = market.get('name', 'Unknown')
                
                print(f"  {i}. {home_team} vs {away_team} - {market_name}")
                
                # Show outcomes
                outcomes = market.get('outcomes', [])
                for outcome in outcomes:
                    name = outcome.get('name', 'N/A')
                    price = outcome.get('price', 'N/A')
                    handicap = outcome.get('handicap', 'N/A')
                    print(f"     - {name} ({handicap}): {price}")
            
            return True, markets
        else:
            print("\n❌ Unexpected API response structure for spread markets")
            print(f"Response: {data}")
            return False, None
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error fetching spread markets: {str(e)}")
        return False, None

def save_sample_data(data, filename):
    """Save sample API response to a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    print(f"\nSaved sample data to {filename}")

def main():
    # Load configuration
    config = load_config()
    if not config:
        # Check if API key is provided as command-line argument
        if len(sys.argv) > 1:
            api_key = sys.argv[1]
        else:
            api_key = input("Enter your SportsGameOdds API key: ")
    else:
        # Try to get API key from config
        try:
            api_key = None
            for sportsbook in config.get('apis', {}).get('sportsbooks', []):
                if sportsbook.get('name') == 'sportsgameodds':
                    api_key = sportsbook.get('api_key')
                    break
                    
            if not api_key:
                api_key = input("API key not found in config. Enter your SportsGameOdds API key: ")
        except Exception as e:
            print(f"Error reading config: {str(e)}")
            api_key = input("Enter your SportsGameOdds API key: ")
    
    print("\n🔍 Testing SportsGameOdds API...")
    
    # Test API connection
    connection_success, sports = test_api_connection(api_key)
    if not connection_success:
        print("❌ API connection failed. Please check your API key and try again.")
        return
    
    # If connection was successful, save sample sports data
    if sports:
        save_sample_data(sports, "sample_sports.json")
    
    # Get soccer matches
    matches_success, matches = get_soccer_matches(api_key)
    if matches_success and matches:
        save_sample_data(matches, "sample_soccer_matches.json")
    
    # Get spread markets
    markets_success, markets = get_spread_markets(api_key)
    if markets_success and markets:
        save_sample_data(markets, "sample_spread_markets.json")
    
    print("\n✅ API testing complete!")
    
    # Update config suggestion
    print("\n📝 Next Steps:")
    print("1. Review the sample JSON files to understand the API response structure")
    print("2. Update your config.yaml file with the SportsGameOdds API key:")
    print("   apis:")
    print("     sportsbooks:")
    print("       - name: \"sportsgameodds\"")
    print("         base_url: \"https://api.sportsgameodds.com/v2\"")
    print(f"         api_key: \"{api_key}\"")

if __name__ == "__main__":
    main()