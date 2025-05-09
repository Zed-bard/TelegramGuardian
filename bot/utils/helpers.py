#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helper utilities for the Telegram Group Manager Bot.
This module contains general helper functions.
"""

import logging
import re
from typing import Dict, Any, Optional

from bot.storage.data import get_user_data, get_group_data

# Set up logging
logger = logging.getLogger(__name__)

def get_user_profile(user_id: int, chat_id: int) -> Dict[str, Any]:
    """
    Get data about a user in a specific chat.
    This is a helper function that combines various data sources.
    
    Args:
        user_id: The user's ID
        chat_id: The chat's ID
        
    Returns:
        Dict: User profile data
    """
    # Get user's global data
    user_data = get_user_data(user_id)
    
    # Get group data
    group_data = get_group_data(chat_id)
    
    # Get permissions dict
    permissions = group_data.get('permissions', {})
    
    # Convert user_id to string for JSON compatibility
    user_id_str = str(user_id)
    
    # Get user's permission level in this chat
    permission_level = permissions.get(user_id_str, 0)
    
    # Combine data into a profile
    profile = {
        'user_id': user_id,
        'permission_level': permission_level,
        'global_data': user_data,
        'warnings': group_data.get('warnings', {}).get(user_id_str, 0),
        'joined_date': group_data.get('member_joined', {}).get(user_id_str, None),
    }
    
    return profile


def format_message(message: str, variables: Dict[str, Any]) -> str:
    """
    Format a message with variables.
    
    Args:
        message: The message template
        variables: The variables to substitute
        
    Returns:
        str: The formatted message
    """
    # Simple variable substitution using format string
    try:
        return message.format(**variables)
    except KeyError as e:
        logger.warning(f"Missing variable in message template: {e}")
        return message
    except Exception as e:
        logger.error(f"Error formatting message: {e}")
        return message


def extract_command_args(text: str, command: str) -> Optional[str]:
    """
    Extract arguments from a command.
    
    Args:
        text: The full message text
        command: The command to extract arguments from
        
    Returns:
        Optional[str]: The arguments, or None if command not found
    """
    if not text:
        return None
    
    # Check if text starts with the command
    if not text.startswith(f"/{command}"):
        return None
    
    # Extract everything after the command
    pattern = rf"^/{command}(?:@\w+)?\s*(.*)"
    match = re.match(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return ""  # Command found, but no arguments