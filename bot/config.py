#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration settings for the Telegram Group Manager Bot.
"""

import os
import json
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Path to the config file
CONFIG_FILE = 'config.json'

# Get bot token from environment variable or config file
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# If not in environment, try to get it from config file
if not BOT_TOKEN:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                BOT_TOKEN = config.get('bot_token')
                if BOT_TOKEN:
                    # Update environment variable for consistency
                    os.environ['TELEGRAM_BOT_TOKEN'] = BOT_TOKEN
        except Exception as e:
            logger.error(f"Error loading token from config file: {e}")

# Constants for permission levels
PERMISSION_LEVELS = {
    'banned': -100,
    'restricted': -10,
    'regular': 0,
    'trusted': 10,
    'moderator': 50,
    'admin': 100,
    'owner': 1000
}

# UI Colors for formatting messages
COLORS = {
    'primary': '🔷',    # Telegram Blue - for primary information and titles
    'secondary': '🔹',  # Light Blue - for secondary information
    'success': '✅',    # Green - for success messages
    'alert': '⚠️',      # Warning Red - for warnings and errors
    'neutral': '⚪',    # Grey - for neutral information
}

# Command descriptions
COMMANDS = {
    'start': 'Introduces the bot and its capabilities',
    'help': 'Shows available commands and usage information',
    'welcome': 'Set or view the welcome message for new members',
    'rules': 'Set or view group rules',
    'promote': 'Promote a user to a higher permission level',
    'demote': 'Demote a user to a lower permission level',
    'ban': 'Ban a user from the group',
    'unban': 'Unban a previously banned user',
    'mute': 'Mute a user temporarily',
    'unmute': 'Unmute a previously muted user',
    'warn': 'Warn a user about inappropriate behavior',
    'settings': 'Configure bot settings for the group',
    'stats': 'View group statistics',
}

# Default configuration
DEFAULT_CONFIG = {
    'moderation_enabled': True,
    'auto_delete': False,
    'welcome_enabled': True,
    'welcome_message': 'Welcome {username} to {group_name}! Please read the group rules.',
    'rules': 'No rules have been set for this group yet.'
}

# Load configuration from file
def load_config():
    """Load configuration from file."""
    config = DEFAULT_CONFIG.copy()
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        else:
            # Save default config if file doesn't exist
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            logger.info(f"Created default configuration file: {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
    
    return config

# Save configuration to file
def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

# Global configuration object
CONFIG = load_config()