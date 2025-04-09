#!/usr/bin/env python3
"""
Script to fetch soccer odds from the Sports Game Odds API.
Uses pagination with cursor to retrieve all results.
"""

import requests
import json
import sys
import yaml
import os
from datetime import datetime, timedelta

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return None
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

def fetch_soccer_events_with_odds(api_key, league=None):
    """
    Fetch soccer events with their odds using pagination.
    
    Args:
        api_key (str): API key for SportsGameOdds
        league (str, optional): Specific soccer league ID
    
    Returns:
        list: List of events with odds
    """
    url = "https://api.sportsgameodds.com/v2/events"
    headers = {
        "X-API-Key": api_key
    }
    
    # Base parameters
    params = {
        "limit": 100,  # Max allowed limit to reduce number of API calls
    }
    
    # Add sport or league filter
    if league:
        params["leagueID"] = league
    else:
        params["sportID"] = "SOCCER"
    
    # Add date range for upcoming events
    today = datetime.now()
    next_week = today + timedelta(days=7)
    params["startsAfter"] = today.strftime("%Y-%m-%d")
    params["startsBefore"] = next_week.strftime("%Y-%m-%d")
    
    print(f"Fetching soccer events from {params['startsAfter']} to {params['startsBefore']}...")
    
    # Use pagination with cursor to get all results
    all_events = []
    next_cursor = None
    page = 1
    
    while True:
        if next_cursor:
            params["cursor"] = next_cursor
        
        try:
            print(f"Fetching page {page} of events...")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            
            if not data.get("success", False):
                print(f"API returned failure: {data}")
                break
            
            events = data.get("data", [])
            print(f"Retrieved {len(events)} events on page {page}")
            
            if not events:
                print("No events found in response")
                break
            
            all_events.extend(events)
            
            # Check if there are more pages
            next_cursor = data.get("nextCursor")
            if not next_cursor:
                print("Reached the end of results")
                break
            
            page += 1
            
        except Exception as e:
            print(f"Error fetching events: {str(e)}")
            break
    
    print(f"Total events retrieved: {len(all_events)}")
    return all_events

def process_and_save_events(events):
    """
    Process events and save to file.
    
    Args:
        events (list): List of events with odds
    
    Returns:
        list: Processed events with odds in a format suitable for analysis
    """
    if not events:
        print("No events to process")
        return []
    
    # Save raw events data
    with open("soccer_events_raw.json", "w") as f:
        json.dump(events, f, indent=2)
    print("Raw events saved to soccer_events_raw.json")
    
    # Process events to extract relevant information
    processed_events = []
    
    for event in events:
        # Print the first event structure to debug
        if len(processed_events) == 0:
            print("\nExample event structure:")
            print(json.dumps({k: "..." for k in event.keys()}, indent=2))
            
            # If we have home/away teams, show their structure
            if 'home' in event:
                print("\nHome team structure:")
                print(json.dumps(event['home'], indent=2))
            if 'away' in event:
                print("\nAway team structure:")
                print(json.dumps(event['away'], indent=2))
        
        # Try different methods to extract team names
        home_team = "Unknown"
        away_team = "Unknown"
        
        # Try different structures to get team names
        if 'home' in event and isinstance(event['home'], dict):
            if 'names' in event['home'] and isinstance(event['home']['names'], dict):
                home_team = event['home']['names'].get('long') or event['home']['names'].get('medium') or event['home']['names'].get('short', 'Unknown')
            elif 'name' in event['home']:
                home_team = event['home']['name']
            elif 'teamID' in event['home']:
                home_team = event['home']['teamID']
                
        if 'away' in event and isinstance(event['away'], dict):
            if 'names' in event['away'] and isinstance(event['away']['names'], dict):
                away_team = event['away']['names'].get('long') or event['away']['names'].get('medium') or event['away']['names'].get('short', 'Unknown')
            elif 'name' in event['away']:
                away_team = event['away']['name']
            elif 'teamID' in event['away']:
                away_team = event['away']['teamID']
                
        # Alternative method: look for teamID directly in event
        if home_team == "Unknown" and 'homeTeamID' in event:
            home_team = event['homeTeamID']
        if away_team == "Unknown" and 'awayTeamID' in event:
            away_team = event['awayTeamID']
            
        # Create processed event object
        processed_event = {
            'id': event.get('id'),
            'homeTeam': home_team,
            'awayTeam': away_team,
            'startTime': event.get('startTime'),
            'league': event.get('leagueID', 'Unknown'),
            'markets': []
        }
        
        # Extract odds information
        odds = event.get('odds', {})
        for odd_id, odd_data in odds.items():
            # For this example, we're simplifying by focusing on basic odds
            market_name = odd_data.get('name', 'Unknown')
            
            # Try to make a more descriptive name if it's unknown
            if market_name == 'Unknown' and '-' in odd_id:
                # Extract information from the odd_id itself
                parts = odd_id.split('-')
                if len(parts) >= 3:
                    market_type = parts[0]  # e.g., "points"
                    team_side = parts[1]    # e.g., "home", "away", "all"
                    time_period = parts[2]  # e.g., "reg" (regulation time)
                    market_name = f"{market_type.capitalize()} {team_side} {time_period}"
            
            processed_market = {
                'type': odd_id,
                'name': market_name,
                'odds': odd_data.get('odds')
            }
            
            processed_event['markets'].append(processed_market)
        
        processed_events.append(processed_event)
    
    # Save processed events
    with open("soccer_events_processed.json", "w") as f:
        json.dump(processed_events, f, indent=2)
    print("Processed events saved to soccer_events_processed.json")
    
    return processed_events

def extract_spread_markets(events):
    """
    Extract spread markets from events for use in the Kalshi Odds Comparison tool.
    
    Args:
        events (list): List of processed events
        
    Returns:
        list: Events with only spread markets
    """
    events_with_spreads = []
    
    for event in events:
        spread_markets = []
        
        # Look for markets that might be spread markets
        for market in event['markets']:
            market_type = market['type'].lower()
            
            # Check for common spread market identifiers
            is_spread = (
                'spread' in market_type or 
                'handicap' in market_type or
                (('home' in market_type or 'away' in market_type) and 
                 ('plus' in market_type or 'minus' in market_type))
            )
            
            # Also check for point spread markets
            if 'points' in market_type and any(x in market_type for x in ['ou', 'over', 'under', 'hdp']):
                is_spread = True
                
            if is_spread:
                spread_markets.append(market)
        
        # If we found spread markets, add this event
        if spread_markets:
            events_with_spreads.append({
                'id': event['id'],
                'homeTeam': event['homeTeam'],
                'awayTeam': event['awayTeam'],
                'startTime': event['startTime'],
                'league': event['league'],
                'markets': spread_markets
            })
    
    # Save spread markets data
    with open("soccer_spread_markets.json", "w") as f:
        json.dump(events_with_spreads, f, indent=2)
    print(f"Found {len(events_with_spreads)} events with spread markets")
    print("Spread markets saved to soccer_spread_markets.json")
    
    return events_with_spreads

def print_events_summary(events):
    """
    Print a summary of the events and their odds.
    
    Args:
        events (list): List of processed events
    """
    print("\n=== Soccer Events Summary ===")
    
    for i, event in enumerate(events[:5], 1):  # Limit to first 5 for display
        print(f"\n{i}. {event['homeTeam']} vs {event['awayTeam']}")
        print(f"   League: {event['league']}")
        print(f"   Start Time: {event['startTime']}")
        print(f"   Available Markets: {len(event['markets'])}")
        
        # Display first few markets as examples
        for j, market in enumerate(event['markets'][:3], 1):
            print(f"     {j}. {market['name']} (Type: {market['type']})")
            if isinstance(market['odds'], (int, float)):
                print(f"        Odds: {market['odds']}")
            elif isinstance(market['odds'], dict):
                for k, v in market['odds'].items():
                    print(f"        {k}: {v}")
            else:
                print(f"        Odds format: {type(market['odds'])}")
    
    if len(events) > 5:
        print(f"\n...and {len(events) - 5} more events")

def main():
    # Load configuration or get API key
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
    
    # Fetch events with odds
    print("\n1. Fetching soccer events")
    events = fetch_soccer_events_with_odds(api_key, "MLS")  # Start with MLS since we know it works
    
    if not events:
        print("\nNo MLS events found. Let's try with other leagues.")
        soccer_leagues = ["EPL", "LA_LIGA", "SERIE_A", "BUNDESLIGA", "LIGUE_1", "CHAMPIONS_LEAGUE"]
        
        for league in soccer_leagues:
            print(f"\nTrying with league: {league}")
            events = fetch_soccer_events_with_odds(api_key, league)
            if events:
                print(f"Found events for {league}!")
                break
    
    if not events:
        print("\nCould not retrieve any soccer events. Please check your API key or try again later.")
        return
    
    # Process events
    print("\n2. Processing events")
    processed_events = process_and_save_events(events)
    
    # Extract spread markets for the Kalshi Odds Comparison tool
    print("\n3. Extracting spread markets")
    spread_events = extract_spread_markets(processed_events)
    
    # Print summary
    print("\n4. Events summary")
    print_events_summary(processed_events)
    
    # Print spread markets summary if available
    if spread_events:
        print("\n5. Spread Markets Summary")
        print_events_summary(spread_events)
    else:
        print("\n5. No spread markets found in the events")

if __name__ == "__main__":
    main()