from telegram import Update, ParseMode
from telegram.ext import (
    CommandHandler, Filters, CallbackContext
)

from bot.utils.permissions import check_permission, update_user_permission
from bot.utils.helpers import get_user_data, format_message
from bot.config import COMMANDS, COLORS, PERMISSION_LEVELS
from bot.storage.data import get_group_data, save_group_data

import logging

logger = logging.getLogger(__name__)

def start_command(update: Update, context: CallbackContext) -> None:
    """Start command handler - introduces the bot and its capabilities."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    if update.effective_chat.type == 'private':
        message = (
            f"{COLORS['primary']} Hello {user.first_name}! I'm Group Manager Bot.\n\n"
            f"I can help manage groups by:\n"
            f"• Welcoming new members\n"
            f"• Managing user permissions\n"
            f"• Moderating content\n"
            f"• Providing automated interactions\n\n"
            f"Add me to a group and make me an admin to get started!"
        )
    else:
        message = (
            f"{COLORS['primary']} Hello! I'm Group Manager Bot.\n\n"
            f"I'm ready to help manage this group. Group admins can use /settings to configure me."
        )
    
    update.message.reply_text(message)


def help_command(update: Update, context: CallbackContext) -> None:
    """Display help information about available commands."""
    user = update.effective_user
    chat = update.effective_chat
    # For now, we'll set a default permission level for simplicity
    # In a real implementation, you'd call check_permission without await
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
    help_text = f"{COLORS['primary']} *Group Manager Bot Commands*\n\n"
    
    for cmd, desc in available_commands.items():
        help_text += f"/{cmd} - {desc}\n"
    
    # We'd get the permission name from a helper function
    # For now, just use a placeholder
    permission_name = "Regular User"
    help_text += f"\n{COLORS['neutral']} Your permission level: {permission_name}"
    
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)


def welcome_command(update: Update, context: CallbackContext) -> None:
    """Set or view the welcome message for new members."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to change welcome message
    # For now, we'll set a default permission level for simplicity
    user_permission = PERMISSION_LEVELS['regular']
    if user_permission < PERMISSION_LEVELS['admin']:
        update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to change the welcome message."
        )
        return
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    # If no arguments provided, show current welcome message
    if not context.args:
        welcome_msg = group_data.get('welcome_message', "No custom welcome message set.")
        update.message.reply_text(
            f"{COLORS['secondary']} Current welcome message:\n\n{welcome_msg}\n\n"
            f"To set a new welcome message, use:\n/welcome Your welcome message here.\n\n"
            f"You can use {'{username}'} to mention the new user and {'{group_name}'} for the group name."
        )
        return
    
    # Set new welcome message
    new_message = ' '.join(context.args)
    group_data['welcome_message'] = new_message
    save_group_data(chat.id, group_data)
    
    update.message.reply_text(
        f"{COLORS['success']} Welcome message updated successfully!"
    )


async def promote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Promote a user to a higher permission level."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to promote others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['admin']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to promote users."
        )
        return
    
    # Check if a user was mentioned
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text(
            f"{COLORS['alert']} Please reply to a user's message or provide a username to promote them."
        )
        return
    
    # Get the target user
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        # Try to get user from username
        # Note: In a real implementation, this would require more complex user lookup
        # For simplicity, we'll just note this limitation
        await update.message.reply_text(
            f"{COLORS['alert']} Promoting by username is not implemented yet. Please reply to a user's message instead."
        )
        return
    
    if not target_user:
        await update.message.reply_text(
            f"{COLORS['alert']} Could not identify the user to promote."
        )
        return
    
    # Get target's current permission
    target_permission = await check_permission(target_user.id, chat.id)
    
    # Cannot promote someone with higher or equal permission
    if target_permission >= user_permission:
        await update.message.reply_text(
            f"{COLORS['alert']} You cannot promote a user with equal or higher permissions than yourself."
        )
        return
    
    # Determine new permission level
    new_level = 'moderator' if target_permission < PERMISSION_LEVELS['moderator'] else 'admin'
    
    # Update the permission
    await update_user_permission(target_user.id, chat.id, PERMISSION_LEVELS[new_level])
    
    await update.message.reply_text(
        f"{COLORS['success']} User {target_user.first_name} has been promoted to {new_level}."
    )


async def demote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Demote a user to a lower permission level."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to demote others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['admin']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to demote users."
        )
        return
    
    # Check if a user was mentioned
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text(
            f"{COLORS['alert']} Please reply to a user's message or provide a username to demote them."
        )
        return
    
    # Get the target user
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        # Try to get user from username (limitation noted, similar to promote)
        await update.message.reply_text(
            f"{COLORS['alert']} Demoting by username is not implemented yet. Please reply to a user's message instead."
        )
        return
    
    if not target_user:
        await update.message.reply_text(
            f"{COLORS['alert']} Could not identify the user to demote."
        )
        return
    
    # Get target's current permission
    target_permission = await check_permission(target_user.id, chat.id)
    
    # Cannot demote someone with higher permission
    if target_permission >= user_permission:
        await update.message.reply_text(
            f"{COLORS['alert']} You cannot demote a user with equal or higher permissions than yourself."
        )
        return
    
    # Determine new permission level
    new_level = 'regular' if target_permission >= PERMISSION_LEVELS['moderator'] else 'restricted'
    
    # Update the permission
    await update_user_permission(target_user.id, chat.id, PERMISSION_LEVELS[new_level])
    
    await update.message.reply_text(
        f"{COLORS['success']} User {target_user.first_name} has been demoted to {new_level}."
    )


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban a user from the group."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to ban others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['admin']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to ban users."
        )
        return
    
    # Check if a user was mentioned
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text(
            f"{COLORS['alert']} Please reply to a user's message or provide a username to ban them."
        )
        return
    
    # Get the target user
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif context.args:
        # Try to get user from username (limitation noted)
        await update.message.reply_text(
            f"{COLORS['alert']} Banning by username is not implemented yet. Please reply to a user's message instead."
        )
        return
    
    if not target_user:
        await update.message.reply_text(
            f"{COLORS['alert']} Could not identify the user to ban."
        )
        return
    
    # Get target's current permission
    target_permission = await check_permission(target_user.id, chat.id)
    
    # Cannot ban someone with higher permission
    if target_permission >= user_permission:
        await update.message.reply_text(
            f"{COLORS['alert']} You cannot ban a user with equal or higher permissions than yourself."
        )
        return
    
    # Update the permission to banned
    await update_user_permission(target_user.id, chat.id, PERMISSION_LEVELS['banned'])
    
    # Actual ban using Telegram API
    try:
        await context.bot.ban_chat_member(chat.id, target_user.id)
        await update.message.reply_text(
            f"{COLORS['success']} User {target_user.first_name} has been banned from the group."
        )
    except Exception as e:
        logger.error(f"Failed to ban user: {e}")
        await update.message.reply_text(
            f"{COLORS['alert']} Failed to ban user: {str(e)}"
        )


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unban a previously banned user."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to unban others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['admin']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to unban users."
        )
        return
    
    # Check if a user ID or username was provided
    if not context.args:
        await update.message.reply_text(
            f"{COLORS['alert']} Please provide a username to unban."
        )
        return
    
    username = context.args[0]
    if username.startswith('@'):
        username = username[1:]  # Remove the @ symbol
    
    # In a real implementation, we would need to look up the user_id from username
    # This is a limitation of the current implementation
    await update.message.reply_text(
        f"{COLORS['alert']} Unbanning by username is not fully implemented. "
        f"The bot would need to have a record of user IDs and usernames."
    )
    
    # Note: A more complete implementation would:
    # 1. Look up the user_id from stored data or Telegram API
    # 2. Use the user_id to unban
    # 3. Update the permission level
    
    # Example of how it would work if we had the user_id:
    # user_id = get_user_id_from_username(username)
    # try:
    #     await context.bot.unban_chat_member(chat.id, user_id)
    #     await update_user_permission(user_id, chat.id, PERMISSION_LEVELS['regular'])
    #     await update.message.reply_text(
    #         f"{COLORS['success']} User @{username} has been unbanned."
    #     )
    # except Exception as e:
    #     logger.error(f"Failed to unban user: {e}")
    #     await update.message.reply_text(
    #         f"{COLORS['alert']} Failed to unban user: {str(e)}"
    #     )


async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View or set group rules."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    # If no arguments provided, show current rules
    if not context.args:
        rules = group_data.get('rules', "No rules have been set for this group.")
        await update.message.reply_text(
            f"{COLORS['secondary']} *Group Rules:*\n\n{rules}\n\n"
            f"Admins can set rules with /rules Your rules here.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Check if user has permission to change rules
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['moderator']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to change the group rules."
        )
        return
    
    # Set new rules
    new_rules = ' '.join(context.args)
    group_data['rules'] = new_rules
    save_group_data(chat.id, group_data)
    
    await update.message.reply_text(
        f"{COLORS['success']} Group rules updated successfully!"
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Configure bot settings for the group."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to change settings
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['admin']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to change bot settings."
        )
        return
    
    # Get current settings
    group_data = get_group_data(chat.id)
    
    # Display current settings
    settings = (
        f"{COLORS['primary']} *Bot Settings for {chat.title}*\n\n"
        f"• Welcome new members: {group_data.get('welcome_enabled', True)}\n"
        f"• Content moderation: {group_data.get('moderation_enabled', True)}\n"
        f"• Auto-delete offensive messages: {group_data.get('auto_delete_enabled', True)}\n\n"
        f"To change a setting, use:\n"
        f"/settings welcome on/off\n"
        f"/settings moderation on/off\n"
        f"/settings autodelete on/off"
    )
    
    # If no arguments provided, just show settings
    if not context.args:
        await update.message.reply_text(settings, parse_mode=ParseMode.MARKDOWN)
        return
    
    # Process setting change
    if len(context.args) != 2:
        await update.message.reply_text(
            f"{COLORS['alert']} Invalid format. Use: /settings [setting] [on/off]"
        )
        return
    
    setting = context.args[0].lower()
    value = context.args[1].lower()
    
    if value not in ['on', 'off']:
        await update.message.reply_text(
            f"{COLORS['alert']} Value must be 'on' or 'off'."
        )
        return
    
    value_bool = (value == 'on')
    
    # Update the specified setting
    if setting == 'welcome':
        group_data['welcome_enabled'] = value_bool
        save_group_data(chat.id, group_data)
        await update.message.reply_text(
            f"{COLORS['success']} Welcome messages are now {'enabled' if value_bool else 'disabled'}."
        )
    elif setting == 'moderation':
        group_data['moderation_enabled'] = value_bool
        save_group_data(chat.id, group_data)
        await update.message.reply_text(
            f"{COLORS['success']} Content moderation is now {'enabled' if value_bool else 'disabled'}."
        )
    elif setting == 'autodelete':
        group_data['auto_delete_enabled'] = value_bool
        save_group_data(chat.id, group_data)
        await update.message.reply_text(
            f"{COLORS['success']} Auto-delete for offensive messages is now {'enabled' if value_bool else 'disabled'}."
        )
    else:
        await update.message.reply_text(
            f"{COLORS['alert']} Unknown setting. Available settings: welcome, moderation, autodelete."
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View group statistics."""
    chat = update.effective_chat
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    # Calculate basic stats
    member_count = await context.bot.get_chat_member_count(chat.id)
    message_count = group_data.get('message_count', 0)
    warnings_issued = group_data.get('warnings_issued', 0)
    users_banned = group_data.get('users_banned', 0)
    
    # Format the stats message
    stats = (
        f"{COLORS['secondary']} *Group Statistics for {chat.title}*\n\n"
        f"• Total members: {member_count}\n"
        f"• Messages processed: {message_count}\n"
        f"• Warnings issued: {warnings_issued}\n"
        f"• Users banned: {users_banned}\n\n"
        f"Group created: {chat.date.strftime('%Y-%m-%d') if chat.date else 'Unknown'}"
    )
    
    await update.message.reply_text(stats, parse_mode=ParseMode.MARKDOWN)


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mute (restrict) a user from sending messages."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to mute others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['moderator']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to mute users."
        )
        return
    
    # Check if a user was mentioned
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text(
            f"{COLORS['alert']} Please reply to a user's message to mute them."
        )
        return
    
    # Get the target user
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        await update.message.reply_text(
            f"{COLORS['alert']} Muting by username is not implemented yet. Please reply to a user's message."
        )
        return
    
    if not target_user:
        await update.message.reply_text(
            f"{COLORS['alert']} Could not identify the user to mute."
        )
        return
    
    # Get target's current permission
    target_permission = await check_permission(target_user.id, chat.id)
    
    # Cannot mute someone with higher permission
    if target_permission >= user_permission:
        await update.message.reply_text(
            f"{COLORS['alert']} You cannot mute a user with equal or higher permissions than yourself."
        )
        return
    
    # Update the permission to restricted
    await update_user_permission(target_user.id, chat.id, PERMISSION_LEVELS['restricted'])
    
    # Actual mute using Telegram API
    try:
        await context.bot.restrict_chat_member(
            chat.id, 
            target_user.id,
            permissions=None,  # Set no permissions (completely restricted)
        )
        await update.message.reply_text(
            f"{COLORS['success']} User {target_user.first_name} has been muted."
        )
    except Exception as e:
        logger.error(f"Failed to mute user: {e}")
        await update.message.reply_text(
            f"{COLORS['alert']} Failed to mute user: {str(e)}"
        )


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unmute a previously muted user."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to unmute others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['moderator']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to unmute users."
        )
        return
    
    # Check if a user was mentioned
    if not update.message.reply_to_message and not context.args:
        await update.message.reply_text(
            f"{COLORS['alert']} Please reply to a user's message to unmute them."
        )
        return
    
    # Get the target user
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        await update.message.reply_text(
            f"{COLORS['alert']} Unmuting by username is not implemented yet. Please reply to a user's message."
        )
        return
    
    if not target_user:
        await update.message.reply_text(
            f"{COLORS['alert']} Could not identify the user to unmute."
        )
        return
    
    # Update the permission to regular
    await update_user_permission(target_user.id, chat.id, PERMISSION_LEVELS['regular'])
    
    # Actual unmute using Telegram API
    try:
        await context.bot.restrict_chat_member(
            chat.id, 
            target_user.id,
            permissions={
                'can_send_messages': True,
                'can_send_media_messages': True,
                'can_send_polls': True,
                'can_send_other_messages': True,
                'can_add_web_page_previews': True,
            },
        )
        await update.message.reply_text(
            f"{COLORS['success']} User {target_user.first_name} has been unmuted."
        )
    except Exception as e:
        logger.error(f"Failed to unmute user: {e}")
        await update.message.reply_text(
            f"{COLORS['alert']} Failed to unmute user: {str(e)}"
        )


async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Warn a user about inappropriate behavior."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to warn others
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['moderator']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to warn users."
        )
        return
    
    # Check if a user was mentioned
    if not update.message.reply_to_message:
        await update.message.reply_text(
            f"{COLORS['alert']} Please reply to a user's message to warn them."
        )
        return
    
    # Get the target user
    target_user = update.message.reply_to_message.from_user
    
    # Get target's current permission
    target_permission = await check_permission(target_user.id, chat.id)
    
    # Cannot warn someone with higher permission
    if target_permission >= user_permission:
        await update.message.reply_text(
            f"{COLORS['alert']} You cannot warn a user with equal or higher permissions than yourself."
        )
        return
    
    # Get reason for warning
    reason = "Inappropriate behavior"
    if context.args:
        reason = ' '.join(context.args)
    
    # Get group data and update warning count
    group_data = get_group_data(chat.id)
    
    # Update user warnings
    user_warnings = group_data.setdefault('user_warnings', {})
    user_warnings[str(target_user.id)] = user_warnings.get(str(target_user.id), 0) + 1
    
    # Update group stats
    group_data['warnings_issued'] = group_data.get('warnings_issued', 0) + 1
    
    save_group_data(chat.id, group_data)
    
    # Get current warning count for the user
    warning_count = user_warnings[str(target_user.id)]
    
    # Warn the user
    await update.message.reply_text(
        f"{COLORS['alert']} {target_user.first_name} has been warned.\n"
        f"Reason: {reason}\n"
        f"Warning count: {warning_count}/3"
    )
    
    # If user has 3 or more warnings, apply automatic restriction
    if warning_count >= 3:
        try:
            await context.bot.restrict_chat_member(
                chat.id, 
                target_user.id,
                permissions=None,  # Set no permissions (completely restricted)
            )
            await update_user_permission(target_user.id, chat.id, PERMISSION_LEVELS['restricted'])
            await update.message.reply_text(
                f"{COLORS['alert']} {target_user.first_name} has reached 3 warnings and has been automatically restricted from sending messages."
            )
        except Exception as e:
            logger.error(f"Failed to restrict user after warnings: {e}")


def get_permission_name(permission_level):
    """Get the name of a permission level from its value."""
    for name, level in PERMISSION_LEVELS.items():
        if level == permission_level:
            return name
    return "unknown"


def register_command_handlers(application):
    """Register all command handlers with the application."""
    # Basic commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Group management commands
    application.add_handler(CommandHandler("welcome", welcome_command))
    application.add_handler(CommandHandler("rules", rules_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # User management commands
    application.add_handler(CommandHandler("promote", promote_command))
    application.add_handler(CommandHandler("demote", demote_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    application.add_handler(CommandHandler("warn", warn_command))
