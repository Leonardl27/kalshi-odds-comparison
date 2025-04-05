"""
Module for comparing odds between sportsbooks and Kalshi markets.
"""

from src.analysis.odds_converter import OddsConverter
from src.utils.logger import setup_logger

logger = setup_logger()

class OddsComparator:
    """Class for comparing odds and identifying opportunities."""
    
    def __init__(self, threshold=5.0):
        """
        Initialize the comparator with a threshold.
        
        Args:
            threshold (float): Minimum percentage difference to consider significant
        """
        self.threshold = threshold
    
    def find_opportunities(self, sportsbook_data, kalshi_markets):
        """
        Find opportunities by comparing sportsbook odds with Kalshi markets.
        
        Args:
            sportsbook_data (dict): Dictionary of sportsbook data by sportsbook name
            kalshi_markets (list): List of Kalshi markets
            
        Returns:
            list: List of opportunity dictionaries
        """
        opportunities = []
        
        # Match sportsbook matches with corresponding Kalshi markets
        for sportsbook_name, matches in sportsbook_data.items():
            for match in matches:
                # Try to find corresponding Kalshi markets
                match_kalshi_markets = self._find_matching_kalshi_markets(match, kalshi_markets)
                
                if not match_kalshi_markets:
                    logger.debug(f"No matching Kalshi markets found for {match['home_team']} vs {match['away_team']}")
                    continue
                
                # Compare odds for each market
                for market in match['markets']:
                    if market['type'] == 'spread':
                        # Check home team spread
                        home_opportunities = self._compare_spread_odds(
                            match=match,
                            sportsbook=sportsbook_name,
                            team='home',
                            spread=market['home_spread'],
                            odds=market['home_odds'],
                            kalshi_markets=match_kalshi_markets
                        )
                        opportunities.extend(home_opportunities)
                        
                        # Check away team spread
                        away_opportunities = self._compare_spread_odds(
                            match=match,
                            sportsbook=sportsbook_name,
                            team='away',
                            spread=market['away_spread'],
                            odds=market['away_odds'],
                            kalshi_markets=match_kalshi_markets
                        )
                        opportunities.extend(away_opportunities)
        
        # Sort opportunities by edge (highest first)
        opportunities.sort(key=lambda x: x['edge_percentage'], reverse=True)
        
        return opportunities
    
    def _find_matching_kalshi_markets(self, match, kalshi_markets):
        """
        Find Kalshi markets that correspond to a sportsbook match.
        
        Args:
            match (dict): Sportsbook match data
            kalshi_markets (list): List of Kalshi markets
            
        Returns:
            list: Matching Kalshi markets
        """
        # In a real implementation, this would be more sophisticated
        # For now, we'll do simple text matching on team names
        
        home_team = match['home_team'].lower()
        away_team = match['away_team'].lower()
        
        matching_markets = []
        
        for market in kalshi_markets:
            title = market['title'].lower()
            subtitle = market['subtitle'].lower()
            
            # Check if both team names appear in the market title or subtitle
            if (home_team in title or home_team in subtitle) and (away_team in title or away_team in subtitle):
                matching_markets.append(market)
        
        return matching_markets
    
    def _compare_spread_odds(self, match, sportsbook, team, spread, odds, kalshi_markets):
        """
        Compare spread odds between a sportsbook and Kalshi markets.
        
        Args:
            match (dict): Sportsbook match data
            sportsbook (str): Sportsbook name
            team (str): 'home' or 'away'
            spread (float): Spread value
            odds (int): American odds
            kalshi_markets (list): Matching Kalshi markets
            
        Returns:
            list: Opportunities found
        """
        opportunities = []
        
        # Calculate implied probability from sportsbook odds
        sportsbook_prob = OddsConverter.american_to_probability(odds)
        
        # Find matching Kalshi markets based on the spread
        team_name = match[f'{team}_team']
        for kalshi_market in kalshi_markets:
            # Check if this Kalshi market matches the spread
            # This is a simplistic approach - in reality, you'd need more sophisticated matching
            if self._is_matching_spread_market(kalshi_market, team_name, spread):
                # Get Kalshi price and implied probability
                kalshi_price = kalshi_market['yes_ask']  # Use 'yes_ask' for conservative comparison
                kalshi_prob = OddsConverter.kalshi_price_to_probability(kalshi_price)
                
                # Calculate edge
                edge = abs(sportsbook_prob - kalshi_prob)
                
                # If edge exceeds threshold, record opportunity
                if edge >= self.threshold:
                    opportunities.append({
                        'match_name': f"{match['home_team']} vs {match['away_team']}",
                        'sportsbook': sportsbook,
                        'sportsbook_market': f"{team_name} {spread:+g}",
                        'sportsbook_odds': odds,
                        'sportsbook_implied_prob': round(sportsbook_prob, 2),
                        'kalshi_contract': kalshi_market['ticker'],
                        'kalshi_price': kalshi_price,
                        'kalshi_implied_prob': round(kalshi_prob, 2),
                        'edge_percentage': round(edge, 2)
                    })
        
        return opportunities
    
    def _is_matching_spread_market(self, kalshi_market, team_name, spread):
        """
        Determine if a Kalshi market matches a specific spread.
        
        Args:
            kalshi_market (dict): Kalshi market data
            team_name (str): Team name
            spread (float): Spread value
            
        Returns:
            bool: True if the market matches the spread
        """
        # This is a placeholder implementation
        # In a real application, you'd need to implement sophisticated matching logic
        
        # Check if team name is in the market title or subtitle
        title = kalshi_market['title'].lower()
        subtitle = kalshi_market['subtitle'].lower()
        team_name_lower = team_name.lower()
        
        if team_name_lower not in title and team_name_lower not in subtitle:
            return False
        
        # Check for spread indicators in the subtitle
        # This is very simplified - real implementation would be more sophisticated
        spread_str = f"{abs(spread)}"
        if spread > 0:
            spread_indicators = ["+", "plus", "more than"]
        else:
            spread_indicators = ["-", "minus", "less than"]
            
        # Check if any spread indicator is in the subtitle along with the spread value
        for indicator in spread_indicators:
            if indicator in subtitle and spread_str in subtitle:
                return True
                
        return False