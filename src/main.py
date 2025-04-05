#!/usr/bin/env python3
"""
Main entry point for the Kalshi Odds Comparison application.
Coordinates data collection, analysis, and reporting.
"""

import argparse
import asyncio
import yaml
import os
from datetime import datetime

from src.data_collection.sportsbook import SportsBookClient
from src.data_collection.sportsgameodds import SportsGameOddsClient
from src.data_collection.kalshi import KalshiClient
from src.analysis.comparator import OddsComparator
from src.utils.logger import setup_logger

logger = setup_logger()

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config

async def collect_data(config):
    """Collect data from sportsbooks and Kalshi."""
    logger.info("Starting data collection...")
    
    # Initialize clients
    kalshi_client = KalshiClient(
        base_url=config['apis']['kalshi']['base_url'],
        email=config['apis']['kalshi']['email'],
        password=config['apis']['kalshi']['password']
    )
    
    sportsbook_clients = []
    for sb_config in config['apis']['sportsbooks']:
        # Create the appropriate client based on the sportsbook name
        if sb_config['name'].lower() == 'sportsgameodds':
            sportsbook_clients.append(
                SportsGameOddsClient(
                    base_url=sb_config['base_url'],
                    api_key=sb_config['api_key']
                )
            )
        else:
            sportsbook_clients.append(
                SportsBookClient(
                    name=sb_config['name'],
                    base_url=sb_config['base_url'],
                    api_key=sb_config['api_key']
                )
            )
    
    # Authenticate with Kalshi
    await kalshi_client.authenticate()
    
    # Get soccer matches from sportsbooks
    sportsbook_data = {}
    for client in sportsbook_clients:
        client_name = getattr(client, 'name', client.__class__.__name__)
        sportsbook_data[client_name] = await client.get_soccer_matches()
    
    # Get Kalshi markets
    kalshi_markets = await kalshi_client.get_soccer_markets()
    
    logger.info(f"Data collection complete. Found {len(kalshi_markets)} Kalshi markets and " 
                f"{sum(len(matches) for matches in sportsbook_data.values())} sportsbook matches.")
    
    # Close all client sessions
    await kalshi_client.close()
    for client in sportsbook_clients:
        await client.close()
    
    return {
        'sportsbook_data': sportsbook_data,
        'kalshi_markets': kalshi_markets
    }

async def analyze_data(data, config):
    """Analyze collected data to identify opportunities."""
    logger.info("Starting data analysis...")
    
    comparator = OddsComparator(threshold=config['analysis']['threshold_percentage'])
    opportunities = comparator.find_opportunities(
        sportsbook_data=data['sportsbook_data'],
        kalshi_markets=data['kalshi_markets']
    )
    
    logger.info(f"Analysis complete. Found {len(opportunities)} potential opportunities.")
    
    return opportunities

def report_results(opportunities):
    """Report identified opportunities."""
    if not opportunities:
        logger.info("No significant opportunities found.")
        return
    
    logger.info(f"Found {len(opportunities)} potential opportunities:")
    for i, opp in enumerate(opportunities, 1):
        logger.info(f"Opportunity #{i}:")
        logger.info(f"  Match: {opp['match_name']}")
        logger.info(f"  Sportsbook: {opp['sportsbook']} ({opp['sportsbook_odds']}, {opp['sportsbook_implied_prob']}%)")
        logger.info(f"  Kalshi: {opp['kalshi_contract']} ({opp['kalshi_price']}, {opp['kalshi_implied_prob']}%)")
        logger.info(f"  Edge: {opp['edge_percentage']:.2f}%")
        logger.info("")

async def main(config_path):
    """Main application flow."""
    # Load configuration
    config = load_config(config_path)
    
    # Set up logging based on config
    logger.info(f"Starting Kalshi Odds Comparison at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Collect data from APIs
        data = await collect_data(config)
        
        # Analyze data to find opportunities
        opportunities = await analyze_data(data, config)
        
        # Report results
        report_results(opportunities)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kalshi Odds Comparison Tool")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")
    args = parser.parse_args()
    
    asyncio.run(main(args.config))