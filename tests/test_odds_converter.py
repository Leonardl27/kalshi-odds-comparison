"""
Tests for the odds_converter module.
"""

import pytest
from src.analysis.odds_converter import OddsConverter

class TestOddsConverter:
    """Test suite for the OddsConverter class."""
    
    def test_american_to_decimal(self):
        """Test converting American odds to decimal."""
        # Test positive American odds
        assert round(OddsConverter.american_to_decimal(100), 2) == 2.00
        assert round(OddsConverter.american_to_decimal(250), 2) == 3.50
        
        # Test negative American odds
        assert round(OddsConverter.american_to_decimal(-110), 2) == 1.91
        assert round(OddsConverter.american_to_decimal(-200), 2) == 1.50
    
    def test_decimal_to_american(self):
        """Test converting decimal odds to American."""
        # Test decimal odds >= 2.0
        assert OddsConverter.decimal_to_american(2.0) == 100
        assert OddsConverter.decimal_to_american(3.5) == 250
        
        # Test decimal odds < 2.0
        assert OddsConverter.decimal_to_american(1.91) == -110
        assert OddsConverter.decimal_to_american(1.5) == -200
    
    def test_decimal_to_probability(self):
        """Test converting decimal odds to probability."""
        assert round(OddsConverter.decimal_to_probability(2.0), 2) == 50.00
        assert round(OddsConverter.decimal_to_probability(1.5), 2) == 66.67
        assert round(OddsConverter.decimal_to_probability(3.0), 2) == 33.33
    
    def test_american_to_probability(self):
        """Test converting American odds to probability."""
        assert round(OddsConverter.american_to_probability(100), 2) == 50.00
        assert round(OddsConverter.american_to_probability(-150), 2) == 60.00
        assert round(OddsConverter.american_to_probability(200), 2) == 33.33
    
    def test_probability_to_decimal(self):
        """Test converting probability to decimal odds."""
        assert round(OddsConverter.probability_to_decimal(50), 2) == 2.00
        assert round(OddsConverter.probability_to_decimal(25), 2) == 4.00
        assert round(OddsConverter.probability_to_decimal(75), 2) == 1.33
    
    def test_kalshi_price_to_probability(self):
        """Test converting Kalshi price to probability."""
        assert OddsConverter.kalshi_price_to_probability(65) == 65.0
        assert OddsConverter.kalshi_price_to_probability(32) == 32.0
        assert OddsConverter.kalshi_price_to_probability(0) == 0.0
        assert OddsConverter.kalshi_price_to_probability(100) == 100.0
    
    def test_probability_to_kalshi_price(self):
        """Test converting probability to Kalshi price."""
        assert OddsConverter.probability_to_kalshi_price(65.4) == 65
        assert OddsConverter.probability_to_kalshi_price(32.1) == 32
        assert OddsConverter.probability_to_kalshi_price(0) == 0
        assert OddsConverter.probability_to_kalshi_price(100) == 100