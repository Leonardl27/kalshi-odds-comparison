"""
Tests for the Kalshi API client.
"""

import pytest
import aiohttp
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.data_collection.kalshi import KalshiClient

class TestKalshiClient:
    """Test suite for the KalshiClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = KalshiClient(
            base_url="https://test-api.kalshi.com/v1",
            email="test@example.com",
            password="password123"
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        # Ensure any session is closed
        if self.client.session:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.client.close())
            else:
                loop.run_until_complete(self.client.close())
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test client initialization."""
        assert self.client.base_url == "https://test-api.kalshi.com/v1"
        assert self.client.email == "test@example.com"
        assert self.client.password == "password123"
        assert self.client.token is None
        assert self.client.session is None
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_authenticate_success(self, mock_post):
        """Test successful authentication."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"token": "test_token_123"})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Call authenticate
        result = await self.client.authenticate()
        
        # Check the result
        assert result is True
        assert self.client.token == "test_token_123"
        
        # Verify the request
        mock_post.assert_called_once_with(
            f"{self.client.base_url}/login",
            json={"email": self.client.email, "password": self.client.password}
        )
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.post')
    async def test_authenticate_failure(self, mock_post):
        """Test failed authentication."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Call authenticate
        result = await self.client.authenticate()
        
        # Check the result
        assert result is False
        assert self.client.token is None
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    @patch('src.data_collection.kalshi.KalshiClient.authenticate')
    async def test_get_soccer_markets(self, mock_authenticate, mock_get):
        """Test getting soccer markets."""
        # Mock authentication
        mock_authenticate.return_value = True
        self.client.token = "test_token_123"
        
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "markets": [
                {
                    "id": "market_1",
                    "ticker": "SOCCER-TEAMA-TEAMB-123",
                    "title": "Team A vs Team B",
                    "subtitle": "Soccer Match",
                    "close_time": "2023-12-01T12:00:00Z",
                    "yes_bid": 42,
                    "yes_ask": 45,
                    "no_bid": 55,
                    "no_ask": 58,
                    "last_price": 44,
                    "volume": 1000
                }
            ]
        })
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Call get_soccer_markets
        markets = await self.client.get_soccer_markets()
        
        # Check the result
        assert len(markets) == 1
        assert markets[0]["id"] == "market_1"
        assert markets[0]["title"] == "Team A vs Team B"
        
        # Verify the request
        mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_get_soccer_markets_not_authenticated(self, mock_get):
        """Test getting soccer markets without authentication."""
        # Set up the client without a token
        self.client.token = None
        
        # Mock authenticate to fail
        with patch.object(self.client, 'authenticate', return_value=False):
            # Call get_soccer_markets
            markets = await self.client.get_soccer_markets()
            
            # Check the result
            assert markets == []
            # Verify no request was made
            mock_get.assert_not_called()