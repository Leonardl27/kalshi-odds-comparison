"""
Tests for the comparator module.
"""

import pytest
from src.analysis.comparator import OddsComparator

class TestOddsComparator:
    """Test suite for the OddsComparator class."""
    
    def setup_method(self):
        """Set up test data."""
        self.comparator = OddsComparator(threshold=5.0)
        
        # Sample sportsbook data
        self.sportsbook_data = {
            'test_sportsbook': [
                {
                    'id': 'match_1',
                    'home_team': 'Team A',
                    'away_team': 'Team B',
                    'start_time': '2023-12-01T12:00:00Z',
                    'competition': 'Test League',
                    'markets': [
                        {
                            'type': 'spread',
                            'home_spread': -1.5,
                            'home_odds': -110,
                            'away_spread': 1.5,
                            'away_odds': -110
                        }
                    ]
                }
            ]
        }
        
        # Sample Kalshi markets
        self.kalshi_markets = [
            {
                'id': 'kalshi_market_1',
                'ticker': 'SOCCER-TEAMA-TEAMB-123',
                'title': 'Team A vs Team B',
                'subtitle': 'Team A to win by 2+ goals',
                'close_time': '2023-12-01T12:00:00Z',
                'yes_bid': 42,
                'yes_ask': 45,
                'no_bid': 55,
                'no_ask': 58,
                'last_price': 44,
                'volume': 1000
            }
        ]
    
    def test_initialization(self):
        """Test OddsComparator initialization."""
        assert self.comparator.threshold == 5.0
        
        # Test default threshold
        default_comparator = OddsComparator()
        assert default_comparator.threshold == 5.0
    
    def test_find_matching_kalshi_markets(self):
        """Test finding matching Kalshi markets."""
        match = self.sportsbook_data['test_sportsbook'][0]
        matching_markets = self.comparator._find_matching_kalshi_markets(match, self.kalshi_markets)
        
        # Should find one matching market
        assert len(matching_markets) == 1
        assert matching_markets[0]['id'] == 'kalshi_market_1'
    
    def test_no_matching_kalshi_markets(self):
        """Test when no matching Kalshi markets are found."""
        # Modified match with different team names
        match = {
            'id': 'match_2',
            'home_team': 'Team C',
            'away_team': 'Team D',
            'start_time': '2023-12-01T12:00:00Z',
            'competition': 'Test League',
            'markets': []
        }
        
        matching_markets = self.comparator._find_matching_kalshi_markets(match, self.kalshi_markets)
        
        # Should find no matching markets
        assert len(matching_markets) == 0
    
    def test_find_opportunities(self):
        """Test finding opportunities."""
        # This is a more comprehensive test that would require mock data
        # and potentially mocking some methods
        opportunities = self.comparator.find_opportunities(
            self.sportsbook_data,
            self.kalshi_markets
        )
        
        # Basic structure check
        assert isinstance(opportunities, list)