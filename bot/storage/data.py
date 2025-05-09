#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data storage for the Telegram Group Manager Bot.
This module provides functions for storing and retrieving data.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Dictionary to store data in memory
# In a real implementation, we would use a database
_data = {
    'groups': {},  # chat_id -> group data
    'users': {}    # user_id -> user data
}

# Path to data file
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'bot_data.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_data() -> None:
    """Load data from file."""
    global _data
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                _data = json.load(f)
            logger.info("Data loaded from file")
        else:
            logger.info("No data file found, starting with empty data")
    except Exception as e:
        logger.error(f"Error loading data: {e}")


def save_data() -> None:
    """Save data to file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(_data, f, indent=2)
        logger.info("Data saved to file")
    except Exception as e:
        logger.error(f"Error saving data: {e}")


def get_group_data(chat_id: int) -> Dict[str, Any]:
    """
    Get data for a specific group chat.
    
    Args:
        chat_id: The chat ID
        
    Returns:
        Dict: The group data
    """
    chat_id_str = str(chat_id)  # Convert to string for JSON compatibility
    
    # Load data if not already loaded
    if not _data['groups']:
        load_data()
    
    # Create empty dict if group not found
    if chat_id_str not in _data['groups']:
        _data['groups'][chat_id_str] = {}
    
    return _data['groups'][chat_id_str]


def save_group_data(chat_id: int, data: Dict[str, Any]) -> bool:
    """
    Save data for a specific group chat.
    
    Args:
        chat_id: The chat ID
        data: The data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        chat_id_str = str(chat_id)  # Convert to string for JSON compatibility
        _data['groups'][chat_id_str] = data
        save_data()
        return True
    except Exception as e:
        logger.error(f"Error saving group data: {e}")
        return False


def get_user_data(user_id: int) -> Dict[str, Any]:
    """
    Get data for a specific user.
    
    Args:
        user_id: The user ID
        
    Returns:
        Dict: The user data
    """
    user_id_str = str(user_id)  # Convert to string for JSON compatibility
    
    # Load data if not already loaded
    if not _data['users']:
        load_data()
    
    # Create empty dict if user not found
    if user_id_str not in _data['users']:
        _data['users'][user_id_str] = {}
    
    return _data['users'][user_id_str]


def save_user_data(user_id: int, data: Dict[str, Any]) -> bool:
    """
    Save data for a specific user.
    
    Args:
        user_id: The user ID
        data: The data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        user_id_str = str(user_id)  # Convert to string for JSON compatibility
        _data['users'][user_id_str] = data
        save_data()
        return True
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        return False


def clear_all_data() -> None:
    """
    Clear all in-memory data.
    Useful for testing or restarting the bot.
    """
    global _data
    _data = {
        'groups': {},
        'users': {}
    }
    logger.info("All data cleared from memory")


# Initialize data on module load
load_data()