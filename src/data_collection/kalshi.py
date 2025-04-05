"""
Kalshi API client for fetching market data.
"""

import aiohttp
import asyncio
import json
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger()

class KalshiClient:
    """Client for interacting with Kalshi API."""
    
    def __init__(self, base_url, email, password):
        """
        Initialize the Kalshi API client.
        
        Args:
            base_url (str): Base URL for Kalshi API
            email (str): Kalshi account email
            password (str): Kalshi account password
        """
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None
        self.session = None
    
    async def authenticate(self):
        """Authenticate with Kalshi API and get access token."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get('token')
                    logger.info("Successfully authenticated with Kalshi API")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to authenticate with Kalshi: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"Error during Kalshi authentication: {str(e)}")
            return False
    
    async def get_soccer_markets(self):
        """
        Fetch soccer-related markets from Kalshi.
        
        Returns:
            list: List of soccer markets
        """
        if not self.token:
            logger.warning("Not authenticated with Kalshi. Attempting to authenticate...")
            success = await self.authenticate()
            if not success:
                return []
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Search for markets related to soccer
        # Note: You might need to adjust this based on Kalshi's actual API structure
        url = f"{self.base_url}/markets"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {
            "status": "open",
            "series_ticker": "SOCCER"  # This is a placeholder - adjust to Kalshi's actual parameter
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', [])
                    logger.info(f"Retrieved {len(markets)} soccer markets from Kalshi")
                    
                    # Process markets to extract relevant information
                    processed_markets = []
                    for market in markets:
                        processed_markets.append({
                            'id': market.get('id'),
                            'ticker': market.get('ticker'),
                            'title': market.get('title'),
                            'subtitle': market.get('subtitle', ''),
                            'close_time': market.get('close_time'),
                            'yes_bid': market.get('yes_bid'),
                            'yes_ask': market.get('yes_ask'),
                            'no_bid': market.get('no_bid'),
                            'no_ask': market.get('no_ask'),
                            'last_price': market.get('last_price'),
                            'volume': market.get('volume')
                        })
                    
                    return processed_markets
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to retrieve markets: {response.status} - {error_text}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {str(e)}")
            return []
    
    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None