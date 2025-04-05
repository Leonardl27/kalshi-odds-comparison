"""
Logging configuration for the application.
This module sets up loggers with appropriate handlers and formatters.
"""

import os
import logging
import yaml
from datetime import datetime

def setup_logger(config_path="config.yaml"):
    """
    Set up and configure a logger instance.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('kalshi_odds')
    logger.setLevel(logging.INFO)  # Default level
    
    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Try to load config and set up file handler if specified
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Set log level from config
            log_level = config.get('logging', {}).get('level', 'INFO').upper()
            logger.setLevel(getattr(logging, log_level))
            console_handler.setLevel(getattr(logging, log_level))
            
            # Set up file handler if log file is specified
            log_file = config.get('logging', {}).get('file')
            if log_file:
                # Create directory for log file if it doesn't exist
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                # Create file handler
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(getattr(logging, log_level))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                
                logger.info(f"Logging to file: {log_file}")
        
        except Exception as e:
            logger.warning(f"Error loading logging configuration: {str(e)}")
            logger.warning("Using default logging configuration")
    
    return logger