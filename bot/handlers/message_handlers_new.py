#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Message handlers for the Telegram Group Manager Bot.
This module contains handlers for non-command messages.
"""

import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, MessageHandler, Filters

from bot.config import COLORS
from bot.storage.data import get_group_data, save_group_data
from bot.utils.moderation import check_message_content

# Set up logging
logger = logging.getLogger(__name__)

def handle_new_chat_members(update: Update, context: CallbackContext) -> None:
    """Welcome new members to the chat."""
    try:
        chat = update.effective_chat
        new_members = update.message.new_chat_members
        
        logger.info(f"New members joined chat {chat.id}: {[member.id for member in new_members]}")
        
        # Skip if the bot itself is being added
        if any(member.id == context.bot.id for member in new_members):
            logger.info(f"Bot was added to chat {chat.id}")
            return
        
        # Get group data
        group_data = get_group_data(chat.id)
        
        # Get welcome message or use default
        welcome_template = group_data.get('welcome_message', 
            "Welcome {username} to {group_name}! Please read the rules.")
        
        # Welcome each new member
        for member in new_members:
            # Format welcome message with member info
            welcome_message = welcome_template.format(
                username=member.first_name,
                group_name=chat.title
            )
            
            # Send welcome message
            try:
                update.message.reply_text(welcome_message)
                logger.info(f"Sent welcome message to user {member.id} in chat {chat.id}")
            except Exception as e:
                logger.error(f"Failed to send welcome message: {e}")
        
        # Update stats
        group_data['member_count'] = group_data.get('member_count', 0) + len(new_members)
        save_group_data(chat.id, group_data)
    except Exception as e:
        logger.error(f"Error handling new chat members: {e}")


def handle_text_message(update: Update, context: CallbackContext) -> None:
    """Handle regular text messages."""
    try:
        chat = update.effective_chat
        message = update.message
        user = update.effective_user
        
        # Skip messages in private chats
        if chat.type == 'private':
            logger.debug(f"Skipping private message from user {user.id}")
            return
        
        # Skip command messages
        if message.text and message.text.startswith('/'):
            return
        
        logger.debug(f"Processing message from user {user.id} in chat {chat.id}")
        
        # Get group data
        chat_id = chat.id
        group_data = get_group_data(chat_id)
        
        # Update message count for stats
        group_data['message_count'] = group_data.get('message_count', 0) + 1
        save_group_data(chat_id, group_data)
        
        # Check message for moderation if enabled
        if group_data.get('moderation_enabled', False):
            moderation_result, reason = check_message_content(message.text)
            
            if not moderation_result:
                logger.info(f"Message from user {user.id} flagged: {reason}")
                
                # Message violates rules
                try:
                    message.reply_text(
                        f"⚠️ Message contains inappropriate content: {reason}\n"
                        f"Please follow group rules."
                    )
                except Exception as e:
                    logger.error(f"Failed to send moderation warning: {e}")
                
                # Auto-delete if enabled
                if group_data.get('auto_delete', False):
                    try:
                        message.delete()
                        logger.info(f"Deleted message from user {user.id} in chat {chat.id}")
                    except Exception as e:
                        logger.error(f"Failed to delete message: {e}")
    except Exception as e:
        logger.error(f"Error handling text message: {e}")


def handle_left_chat_member(update: Update, context: CallbackContext) -> None:
    """Handle when a member leaves the chat."""
    try:
        chat = update.effective_chat
        user = update.message.left_chat_member
        
        logger.info(f"User {user.id} left chat {chat.id}")
        
        # Skip if the bot itself is leaving
        if user.id == context.bot.id:
            logger.info(f"Bot was removed from chat {chat.id}")
            return
        
        # Get group data
        group_data = get_group_data(chat.id)
        
        # Update stats
        group_data['member_count'] = max(0, group_data.get('member_count', 1) - 1)
        save_group_data(chat.id, group_data)
        
        logger.info(f"Updated stats for chat {chat.id}, member count: {group_data['member_count']}")
    except Exception as e:
        logger.error(f"Error handling left chat member: {e}")


def register_message_handlers(dispatcher):
    """Register all message handlers with the application."""
    # New chat members handler
    dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_new_chat_members))
    
    # Text message handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))
    
    # Left chat member handler
    dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member, handle_left_chat_member))
    
    # Log registration
    logger.info("Message handlers registered")