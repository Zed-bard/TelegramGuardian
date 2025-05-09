from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, filters
)

from bot.utils.permissions import check_permission
from bot.utils.moderation import check_message_content
from bot.utils.helpers import get_user_data, format_message
from bot.config import COLORS, PERMISSION_LEVELS, DEFAULT_WELCOME_MESSAGE
from bot.storage.data import get_group_data, save_group_data

import logging

logger = logging.getLogger(__name__)

async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome new members to the chat."""
    chat = update.effective_chat
    new_members = update.message.new_chat_members
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    # Check if welcome messages are enabled
    if not group_data.get('welcome_enabled', True):
        return
    
    # Get custom welcome message if set, otherwise use default
    welcome_message = group_data.get('welcome_message', DEFAULT_WELCOME_MESSAGE)
    
    # Welcome each new member
    for new_member in new_members:
        # Skip if the new member is the bot itself
        if new_member.id == context.bot.id:
            continue
        
        # Format the welcome message with user info
        formatted_message = welcome_message.format(
            username=new_member.first_name,
            group_name=chat.title
        )
        
        # Send the welcome message
        await context.bot.send_message(
            chat_id=chat.id,
            text=formatted_message
        )
        
        # Set initial permission level for new user
        # This would be handled by permissions.py


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    user = update.effective_user
    chat = update.effective_chat
    message = update.message.text
    
    # Skip processing in private chats
    if chat.type == 'private':
        return
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    # Update message count for statistics
    group_data['message_count'] = group_data.get('message_count', 0) + 1
    save_group_data(chat.id, group_data)
    
    # Check user's permission level
    user_permission = await check_permission(user.id, chat.id)
    
    # If user is banned or restricted, consider deleting their message
    if user_permission <= PERMISSION_LEVELS['restricted']:
        # For banned users, delete messages
        if user_permission == PERMISSION_LEVELS['banned']:
            await update.message.delete()
            return
    
    # Check message content for moderation if enabled
    if group_data.get('moderation_enabled', True):
        is_appropriate, reason = await check_message_content(message)
        
        if not is_appropriate:
            logger.info(f"Inappropriate content detected: {reason}")
            
            # If auto-delete is enabled, delete the message
            if group_data.get('auto_delete_enabled', True):
                try:
                    await update.message.delete()
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text=f"{COLORS['alert']} A message was removed due to inappropriate content: {reason}"
                    )
                except Exception as e:
                    logger.error(f"Failed to delete inappropriate message: {e}")
            else:
                # Just warn about the content
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"{COLORS['alert']} @{user.username or user.first_name}, please avoid inappropriate content: {reason}"
                )


async def handle_left_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle when a member leaves the chat."""
    chat = update.effective_chat
    left_member = update.message.left_chat_member
    
    # Skip if the left member is the bot itself
    if left_member.id == context.bot.id:
        return
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    # Check if goodbye messages are enabled (could be a setting)
    if not group_data.get('goodbye_enabled', False):
        return
    
    # Get custom goodbye message if set, otherwise use default
    goodbye_message = group_data.get('goodbye_message', 
        f"{COLORS['neutral']} {left_member.first_name} has left the group. Farewell!")
    
    # Send the goodbye message
    await context.bot.send_message(
        chat_id=chat.id,
        text=goodbye_message
    )


def register_message_handlers(application):
    """Register all message handlers with the application."""
    # New chat members handler
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))
    
    # Left chat member handler
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_left_chat_member))
    
    # Text message handler - should be added last since it's the most general
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
