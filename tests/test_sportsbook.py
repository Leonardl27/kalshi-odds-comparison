"""
Tests for the sportsbook API client.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from src.data_collection.sportsbook import SportsBookClient

class TestSportsBookClient:
    """Test suite for the SportsBookClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = SportsBookClient(
            name="test_sportsbook",
            base_url="https://api.test-sportsbook.com",
            api_key="test_api_key_123"
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
    
    def test_initialization(self):
        """Test client initialization."""
        assert self.client.name == "test_sportsbook"
        assert self.client.base_url == "https://api.test-sportsbook.com"
        assert self.client.api_key == "test_api_key_123"
        assert self.client.session is None
    
    @pytest.mark.asyncio
    async def test_get_session(self):
        """Test getting a session."""
        session = await self.client._get_session()
        assert session is not None
        assert self.client.session is not None
        
        # Calling again should return the same session
        session2 = await self.client._get_session()
        assert session2 is session
    
    @pytest.mark.asyncio
    async def test_get_soccer_matches(self):
        """Test getting soccer matches."""
        # Mock the _get_session method
        with patch.object(self.client, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_get_session.return_value = mock_session
            
            # Get matches
            matches = await self.client.get_soccer_matches()
            
            # Check if _get_session was called
            mock_get_session.assert_called_once()
            
            # Since we're using mock data, check if we got some matches
            assert isinstance(matches, list)
            assert len(matches) > 0
            
            # Verify match structure
            for match in matches:
                assert 'id' in match
                assert 'home_team' in match
                assert 'away_team' in match
                assert 'start_time' in match
                assert 'competition' in match
                assert 'markets' in match
                
                # Verify markets structure
                for market in match['markets']:
                    assert 'type' in market
                    assert market['type'] == 'spread'
                    assert 'home_spread' in market
                    assert 'home_odds' in market
                    assert 'away_spread' in market
                    assert 'away_odds' in market
    
    def test_mock_soccer_data(self):
        """Test the mock soccer data generator."""
        data = self.client._mock_soccer_data()
        
        # Check if we got mock data
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify data structure
        match = data[0]
        assert 'id' in match
        assert 'home_team' in match
        assert 'away_team' in match
        assert 'start_time' in match
        assert 'competition' in match
        assert 'markets' in match
        
        # Verify markets
        market = match['markets'][0]
        assert market['type'] == 'spread'
        assert 'home_spread' in market
        assert 'home_odds' in market
        assert 'away_spread' in market
        assert 'away_odds' in market
    
    @pytest.mark.asyncio
    async def test_process_matches(self):
        """Test processing raw API response."""
        # Sample API response
        raw_data = {
            "events": [
                {
                    "id": "event_1",
                    "home_team": "Home Team",
                    "away_team": "Away Team",
                    "start_time": "2023-12-01T12:00:00Z",
                    "competition": "Test League",
                    "markets": [
                        {
                            "type": "spread",
                            "home_spread": -1.5,
                            "home_odds": -110,
                            "away_spread": 1.5,
                            "away_odds": -110
                        }
                    ]
                }
            ]
        }
        
        # Process the data
        processed = self.client._process_matches(raw_data)
        
        # Verify processed data
        assert len(processed) == 1
        match = processed[0]
        assert match['id'] == "event_1"
        assert match['home_team'] == "Home Team"
        assert match['away_team'] == "Away Team"
        assert match['start_time'] == "2023-12-01T12:00:00Z"
        assert match['competition'] == "Test League"
        
        # Verify markets
        assert len(match['markets']) == 1
        market = match['markets'][0]
        assert market['type'] == "spread"
        assert market['home_spread'] == -1.5
        assert market['home_odds'] == -110
        assert market['away_spread'] == 1.5
        assert market['away_odds'] == -110