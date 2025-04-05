"""
Module for converting between different odds formats and calculating implied probabilities.
"""

class OddsConverter:
    """Utility class for converting between different odds formats."""
    
    @staticmethod
    def american_to_decimal(american_odds):
        """
        Convert American odds to decimal odds.
        
        Args:
            american_odds (int): Odds in American format (e.g., -110, +240)
            
        Returns:
            float: Odds in decimal format
        """
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    @staticmethod
    def decimal_to_american(decimal_odds):
        """
        Convert decimal odds to American odds.
        
        Args:
            decimal_odds (float): Odds in decimal format
            
        Returns:
            int: Odds in American format
        """
        if decimal_odds >= 2:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    @staticmethod
    def decimal_to_probability(decimal_odds):
        """
        Convert decimal odds to implied probability.
        
        Args:
            decimal_odds (float): Odds in decimal format
            
        Returns:
            float: Implied probability as a percentage (0-100)
        """
        return (1 / decimal_odds) * 100
    
    @staticmethod
    def american_to_probability(american_odds):
        """
        Convert American odds to implied probability.
        
        Args:
            american_odds (int): Odds in American format
            
        Returns:
            float: Implied probability as a percentage (0-100)
        """
        decimal = OddsConverter.american_to_decimal(american_odds)
        return OddsConverter.decimal_to_probability(decimal)
    
    @staticmethod
    def probability_to_decimal(probability):
        """
        Convert probability to decimal odds.
        
        Args:
            probability (float): Probability as a percentage (0-100)
            
        Returns:
            float: Odds in decimal format
        """
        return 100 / probability
    
    @staticmethod
    def kalshi_price_to_probability(price):
        """
        Convert Kalshi price to implied probability.
        
        Args:
            price (int): Kalshi price (e.g., 65 means $0.65)
            
        Returns:
            float: Implied probability as a percentage (0-100)
        """
        # Kalshi prices are in cents (0-100), which directly correlate to probability
        return float(price)
    
    @staticmethod
    def probability_to_kalshi_price(probability):
        """
        Convert probability to Kalshi price.
        
        Args:
            probability (float): Probability as a percentage (0-100)
            
        Returns:
            int: Kalshi price (0-100)
        """
        return int(round(probability))