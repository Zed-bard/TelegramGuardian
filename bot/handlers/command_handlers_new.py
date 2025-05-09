#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command handlers for the Telegram Group Manager Bot.
This module contains handlers for bot commands.
"""

import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler

from bot.config import COLORS, PERMISSION_LEVELS, COMMANDS
from bot.storage.data import get_group_data, save_group_data

# Set up logging
logger = logging.getLogger(__name__)

def start_command(update: Update, context: CallbackContext) -> None:
    """Start command handler - introduces the bot and its capabilities."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log the command received
    logger.info(f"Received /start command from user: {user.id} in chat: {chat.id}")
    
    if chat.type == 'private':
        message = (
            f"👋 Hello {user.first_name}! I'm the Telegram Group Manager Bot.\n\n"
            f"I can help manage groups by:\n"
            f"• Welcoming new members\n"
            f"• Managing user permissions\n"
            f"• Moderating content\n"
            f"• Providing automated interactions\n\n"
            f"Add me to a group and make me an admin to get started!"
        )
    else:
        message = (
            f"👋 Hello! I'm the Telegram Group Manager Bot.\n\n"
            f"I'm ready to help manage this group. Group admins can use /settings to configure me."
        )
    
    try:
        update.message.reply_text(message)
        logger.info(f"Successfully sent response to /start command to user: {user.id}")
    except Exception as e:
        logger.error(f"Error responding to /start command: {e}")


def help_command(update: Update, context: CallbackContext) -> None:
    """Display help information about available commands."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log the command received
    logger.info(f"Received /help command from user: {user.id} in chat: {chat.id}")
    
    # For now, we'll set a default permission level for simplicity
    # In a real implementation, you'd call a non-async version of check_permission
    user_permission = PERMISSION_LEVELS['regular']
    
    # Create a list of available commands based on user's permission level
    available_commands = {}
    
    # Admin commands
    admin_commands = ['promote', 'demote', 'ban', 'unban', 'mute', 'unmute', 'welcome', 'settings']
    
    # Moderator commands
    moderator_commands = ['warn', 'rules']
    
    # All users commands
    all_user_commands = ['start', 'help', 'stats']
    
    # Filter commands based on permission level
    for cmd, desc in COMMANDS.items():
        if user_permission >= PERMISSION_LEVELS['admin'] or (
            cmd in all_user_commands or 
            (cmd in moderator_commands and user_permission >= PERMISSION_LEVELS['moderator'])
        ):
            available_commands[cmd] = desc
    
    # Format the help message
    help_text = "📋 *Group Manager Bot Commands*\n\n"
    
    for cmd, desc in available_commands.items():
        help_text += f"/{cmd} - {desc}\n"
    
    # Get permission name based on level
    permission_names = {
        PERMISSION_LEVELS['owner']: "Owner",
        PERMISSION_LEVELS['admin']: "Admin",
        PERMISSION_LEVELS['moderator']: "Moderator",
        PERMISSION_LEVELS['regular']: "Regular User",
        PERMISSION_LEVELS['restricted']: "Restricted User",
        PERMISSION_LEVELS['banned']: "Banned"
    }
    permission_name = permission_names.get(user_permission, "Regular User")
    
    help_text += f"\nℹ️ Your permission level: {permission_name}"
    
    try:
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Successfully sent response to /help command to user: {user.id}")
    except Exception as e:
        logger.error(f"Error responding to /help command: {e}")


def welcome_command(update: Update, context: CallbackContext) -> None:
    """Set or view the welcome message for new members."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log the command received
    logger.info(f"Received /welcome command from user: {user.id} in chat: {chat.id}")
    
    try:
        # For demonstration, we'll allow all users to view/set welcome messages
        # In a real implementation, you'd check permissions
        
        # Get group data
        group_data = get_group_data(chat.id)
        
        # If no arguments provided, show current welcome message
        if not context.args:
            welcome_msg = group_data.get('welcome_message', "No custom welcome message set.")
            update.message.reply_text(
                f"👋 Current welcome message:\n\n{welcome_msg}\n\n"
                f"To set a new welcome message, use:\n/welcome Your welcome message here.\n\n"
                f"You can use {'{username}'} to mention the new user and {'{group_name}'} for the group name."
            )
            logger.info(f"Successfully showed welcome message to user: {user.id}")
            return
        
        # Set new welcome message
        new_message = ' '.join(context.args)
        group_data['welcome_message'] = new_message
        save_group_data(chat.id, group_data)
        
        update.message.reply_text(
            f"✅ Welcome message updated successfully!"
        )
        logger.info(f"User {user.id} updated welcome message in chat {chat.id}")
    except Exception as e:
        logger.error(f"Error handling /welcome command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your command. Please try again later.")
        except:
            pass


def rules_command(update: Update, context: CallbackContext) -> None:
    """View or set group rules."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log the command received
    logger.info(f"Received /rules command from user: {user.id} in chat: {chat.id}")
    
    try:
        # Get group data
        group_data = get_group_data(chat.id)
        
        # If no arguments provided, show current rules
        if not context.args:
            rules = group_data.get('rules', "No rules have been set for this group.")
            update.message.reply_text(
                f"📜 *Group Rules:*\n\n{rules}\n\n"
                f"Admins can set rules with /rules Your rules here.",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Successfully showed rules to user: {user.id}")
            return
        
        # For demonstration, we'll allow all users to set rules
        # In a real implementation, you'd check permissions
        
        # Set new rules
        new_rules = ' '.join(context.args)
        group_data['rules'] = new_rules
        save_group_data(chat.id, group_data)
        
        update.message.reply_text(
            f"✅ Group rules updated successfully!"
        )
        logger.info(f"User {user.id} updated rules in chat {chat.id}")
    except Exception as e:
        logger.error(f"Error handling /rules command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your command. Please try again later.")
        except:
            pass


def stats_command(update: Update, context: CallbackContext) -> None:
    """View group statistics."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Log the command received
    logger.info(f"Received /stats command from user: {user.id} in chat: {chat.id}")
    
    try:
        # Get group data
        group_data = get_group_data(chat.id)
        
        # Increment the command counter
        command_count = group_data.get('command_count', 0) + 1
        group_data['command_count'] = command_count
        save_group_data(chat.id, group_data)
        
        # Simple stats for demonstration
        stats_text = (
            f"📊 *Group Statistics*\n\n"
            f"Group Name: {chat.title}\n"
            f"Group ID: {chat.id}\n"
        )
        
        # Try to get member count
        try:
            member_count = context.bot.get_chat_member_count(chat.id)
            stats_text += f"Members: {member_count}\n"
        except:
            stats_text += f"Members: Not available in this chat type\n"
        
        # Add message and command counts
        stats_text += (
            f"Messages: {group_data.get('message_count', 0)}\n"
            f"Commands used: {command_count}\n"
        )
        
        update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"Successfully sent stats to user: {user.id} in chat: {chat.id}")
    except Exception as e:
        logger.error(f"Error handling /stats command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your command. Please try again later.")
        except:
            pass


def register_command_handlers(dispatcher):
    """Register all command handlers with the application."""
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("welcome", welcome_command))
    dispatcher.add_handler(CommandHandler("rules", rules_command))
    dispatcher.add_handler(CommandHandler("stats", stats_command))
    
    # Log registration
    logger.info("Command handlers registered")