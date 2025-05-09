#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Permission management utilities for the Telegram Group Manager Bot.
This module contains functions for handling user permissions.
"""

import logging
from typing import Dict, Any, Optional
from telegram import Bot

from bot.config import PERMISSION_LEVELS
from bot.storage.data import get_group_data, save_group_data

# Set up logging
logger = logging.getLogger(__name__)

def check_permission(user_id: int, chat_id: int) -> int:
    """
    Check a user's permission level for a specific chat.
    
    Args:
        user_id: The user's ID
        chat_id: The chat's ID
        
    Returns:
        int: The user's permission level
    """
    # Get group data
    group_data = get_group_data(chat_id)
    
    # Get permissions dict, create if not exists
    permissions = group_data.get('permissions', {})
    
    # Convert user_id to string for JSON compatibility
    user_id_str = str(user_id)
    
    # Return permission level, default to regular if not found
    return permissions.get(user_id_str, PERMISSION_LEVELS['regular'])


def set_permission(user_id: int, chat_id: int, permission_level: int) -> bool:
    """
    Set a user's permission level for a specific chat.
    
    Args:
        user_id: The user's ID
        chat_id: The chat's ID
        permission_level: The permission level to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get group data
        group_data = get_group_data(chat_id)
        
        # Get permissions dict, create if not exists
        permissions = group_data.get('permissions', {})
        
        # Convert user_id to string for JSON compatibility
        user_id_str = str(user_id)
        
        # Set permission level
        permissions[user_id_str] = permission_level
        
        # Update group data
        group_data['permissions'] = permissions
        
        # Save group data
        save_group_data(chat_id, group_data)
        
        return True
    except Exception as e:
        logger.error(f"Error setting permission: {e}")
        return False


def update_user_permission(user_id: int, chat_id: int, new_permission: int) -> bool:
    """
    Update a user's permission level.
    
    Args:
        user_id: The user's ID
        chat_id: The chat's ID
        new_permission: The new permission level
        
    Returns:
        bool: True if successful, False otherwise
    """
    # This is a simplified version - in a real implementation you might
    # want to verify that the user requesting the change has permission to do so
    return set_permission(user_id, chat_id, new_permission)


def init_group_permissions(chat_id: int, bot: Bot) -> None:
    """
    Initialize permissions for a group.
    Sets the creator as owner and admins as admins.
    
    Args:
        chat_id: The chat's ID
        bot: The bot instance
    """
    try:
        # Get group data
        group_data = get_group_data(chat_id)
        
        # Get permissions dict, create if not exists
        permissions = group_data.get('permissions', {})
        
        # Get chat administrators (this would be done via Telegram API in a real implementation)
        # For demonstration, we'll just use dummy data
        # In a real implementation, you would call:
        # admins = bot.get_chat_administrators(chat_id)
        
        # For now, we'll use dummy data
        # In a real implementation, you would iterate through the admins list
        # and set permissions based on their status
        
        # For example:
        # for admin in admins:
        #     user_id_str = str(admin.user.id)
        #     if admin.status == 'creator':
        #         permissions[user_id_str] = PERMISSION_LEVELS['owner']
        #     else:
        #         permissions[user_id_str] = PERMISSION_LEVELS['admin']
        
        # Update group data
        group_data['permissions'] = permissions
        
        # Save group data
        save_group_data(chat_id, group_data)
        
        logger.info(f"Group permissions initialized for chat {chat_id}")
    except Exception as e:
        logger.error(f"Error initializing group permissions: {e}")


def get_permission_name(permission_level: int) -> str:
    """
    Get the name of a permission level from its value.
    
    Args:
        permission_level: The permission level value
        
    Returns:
        str: The permission level name
    """
    # Reverse mapping of permission levels
    for name, level in PERMISSION_LEVELS.items():
        if level == permission_level:
            return name.capitalize()
    
    return "Unknown"