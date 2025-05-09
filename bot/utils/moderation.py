#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Content moderation utilities for the Telegram Group Manager Bot.
This module contains functions for checking and moderating content.
"""

import re
import logging
from typing import Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Predefined list of inappropriate terms
# This is a simplified example - in a real implementation, you might
# want to use more sophisticated techniques or external APIs
INAPPROPRIATE_TERMS = [
    r'\b(badword1|badword2|badword3)\b',  # Example placeholder pattern
    # Add more patterns here
]

def check_message_content(message: str) -> Tuple[bool, str]:
    """
    Check if message content is appropriate based on configured patterns.
    
    Args:
        message: The message text to check
        
    Returns:
        Tuple[bool, str]: (is_appropriate, reason)
            - is_appropriate: True if content is appropriate, False otherwise
            - reason: The reason why content is inappropriate, empty if appropriate
    """
    if not message:
        return True, ""
    
    # Convert to lowercase for case-insensitive matching
    message_lower = message.lower()
    
    # Check against inappropriate terms
    for pattern in INAPPROPRIATE_TERMS:
        match = re.search(pattern, message_lower)
        if match:
            matched_term = match.group(0)
            return False, f"Contains inappropriate term: {matched_term}"
    
    # If we get here, the message is considered appropriate
    return True, ""


def check_media_content(file_id: str, file_type: str) -> Tuple[bool, str]:
    """
    Check if media content is appropriate.
    
    Note: This is a placeholder function. In a real implementation,
    you might use external APIs for image/media analysis.
    
    Args:
        file_id: The file ID to check
        file_type: The type of file (photo, video, etc.)
        
    Returns:
        Tuple[bool, str]: (is_appropriate, reason)
    """
    # This is just a dummy implementation
    logger.info(f"Checking media content: {file_type} (ID: {file_id})")
    
    # In a real implementation, you might download the file and analyze it
    # or send it to an external API for content moderation
    
    # For now, we'll just return that all media is appropriate
    return True, ""