"""
SportsGameOdds API client for fetching sports betting data.
This module handles the specific structure of the SportsGameOdds API.
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from src.utils.logger import setup_logger

logger = setup_logger()

class SportsGameOddsClient:
    """Client for interacting with the SportsGameOdds API."""
    
    def __init__(self, base_url, api_key):
        """
        Initialize the SportsGameOdds API client.
        
        Args:
            base_url (str): Base URL for the SportsGameOdds API
            api_key (str): API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
    
    async def _get_session(self):
        """Get or create an HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_soccer_matches(self):
        """
        Fetch upcoming soccer matches with spread odds.
        
        Returns:
            list: List of soccer matches with odds information
        """
        session = await self._get_session()
        
        # Endpoints for the SportsGameOdds API
        events_endpoint = "/events"
        
        headers = {"X-API-Key": self.api_key}
        
        # Parameters for retrieving soccer matches with odds
        params = {
            "sportId": "SOCCER",  # Using sport ID
            "status": "UPCOMING",
            "includeMarkets": "true",
            "marketTypes": "SPREAD"  # Focus on spread bets
        }
        
        events_url = f"{self.base_url}{events_endpoint}"
        
        try:
            async with session.get(events_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if the response has the expected structure
                    if 'data' in data and isinstance(data['data'], list) and data.get('success', False):
                        processed_matches = self._process_matches(data['data'])
                        logger.info(f"Retrieved {len(processed_matches)} soccer matches from SportsGameOdds API")
                        return processed_matches
                    else:
                        logger.error(f"Unexpected API response structure: {data}")
                        return []
                else:
                    error_text = await response.text()
                    logger.error(f"Error fetching from SportsGameOdds: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching matches from SportsGameOdds: {str(e)}")
            return []
    
    def _process_matches(self, events):
        """
        Process raw API response into standardized match data.
        
        Args:
            events (list): Raw API response data list
            
        Returns:
            list: Processed match data
        """
        matches = []
        
        for event in events:
            # Extract basic match information
            match = {
                'id': event.get('id'),
                'home_team': event.get('homeTeam', {}).get('name'),
                'away_team': event.get('awayTeam', {}).get('name'),
                'start_time': event.get('startTime'),
                'competition': event.get('competition', {}).get('name'),
                'markets': []
            }
            
            # Extract markets/odds - focus on spread markets
            for market in event.get('markets', []):
                if market.get('marketType') == 'SPREAD':
                    spread_market = {
                        'type': 'spread'
                    }
                    
                    # Process outcomes to extract home and away spreads
                    for outcome in market.get('outcomes', []):
                        team_name = outcome.get('name')
                        handicap = outcome.get('handicap')
                        price = outcome.get('price')
                        
                        # Convert price format if necessary
                        if isinstance(price, str) and price.startswith('-'):
                            # American odds format
                            odds = int(price)
                        elif isinstance(price, str) and price.startswith('+'):
                            # American odds format with explicit plus
                            odds = int(price[1:])
                        elif isinstance(price, (int, float)):
                            # Decimal odds format - convert to American
                            from src.analysis.odds_converter import OddsConverter
                            odds = OddsConverter.decimal_to_american(float(price))
                        else:
                            # Default case
                            odds = 0
                        
                        # Determine if this is home or away outcome
                        if team_name == match['home_team']:
                            spread_market['home_spread'] = float(handicap) if handicap else 0.0
                            spread_market['home_odds'] = odds
                        elif team_name == match['away_team']:
                            spread_market['away_spread'] = float(handicap) if handicap else 0.0
                            spread_market['away_odds'] = odds
                    
                    # Only add market if we have both home and away odds
                    if 'home_spread' in spread_market and 'away_spread' in spread_market:
                        match['markets'].append(spread_market)
            
            # Only add matches that have spread markets
            if match['markets']:
                matches.append(match)
        
        return matches
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None