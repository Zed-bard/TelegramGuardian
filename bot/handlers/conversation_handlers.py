from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, 
    CallbackQueryHandler, MessageHandler, filters
)

from bot.utils.permissions import check_permission
from bot.config import COLORS, PERMISSION_LEVELS
from bot.storage.data import get_group_data, save_group_data

import logging

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_ACTION, TYPING_REPLY, TYPING_CHOICE = range(3)

# Callback data
WELCOME_SETUP, RULES_SETUP, FINISH_SETUP = range(3)


async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the interactive setup conversation for the bot."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Check if user has permission to run setup
    user_permission = await check_permission(user.id, chat.id)
    if user_permission < PERMISSION_LEVELS['admin']:
        await update.message.reply_text(
            f"{COLORS['alert']} You don't have permission to run the bot setup."
        )
        return ConversationHandler.END
    
    # Create keyboard for setup options
    keyboard = [
        [
            InlineKeyboardButton("Set Welcome Message", callback_data=str(WELCOME_SETUP)),
            InlineKeyboardButton("Set Group Rules", callback_data=str(RULES_SETUP)),
        ],
        [
            InlineKeyboardButton("Finish Setup", callback_data=str(FINISH_SETUP)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{COLORS['primary']} Welcome to the Group Manager Bot setup!\n\n"
        f"Please select an option to configure:",
        reply_markup=reply_markup
    )
    
    return SELECTING_ACTION


async def welcome_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the welcome message setup."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"{COLORS['secondary']} Please enter the welcome message you'd like to use.\n\n"
        f"You can use these placeholders:\n"
        f"- {{username}} - The new member's name\n"
        f"- {{group_name}} - The name of this group\n\n"
        f"Example: Welcome {{username}} to {{group_name}}! Please read our rules."
    )
    
    # Store the current setup step
    context.user_data['setup_step'] = 'welcome'
    
    return TYPING_REPLY


async def rules_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the group rules setup."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"{COLORS['secondary']} Please enter the rules for your group.\n\n"
        f"These will be shown to users when they use the /rules command."
    )
    
    # Store the current setup step
    context.user_data['setup_step'] = 'rules'
    
    return TYPING_REPLY


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save the user's input based on the current setup step."""
    user_text = update.message.text
    chat = update.effective_chat
    setup_step = context.user_data.get('setup_step')
    
    # Get group data
    group_data = get_group_data(chat.id)
    
    if setup_step == 'welcome':
        group_data['welcome_message'] = user_text
        save_group_data(chat.id, group_data)
        
        await update.message.reply_text(
            f"{COLORS['success']} Welcome message saved successfully!\n\n"
            f"Preview: {user_text.format(username='John', group_name=chat.title)}"
        )
    
    elif setup_step == 'rules':
        group_data['rules'] = user_text
        save_group_data(chat.id, group_data)
        
        await update.message.reply_text(
            f"{COLORS['success']} Group rules saved successfully!\n\n"
            f"Users can now view these rules with the /rules command."
        )
    
    # Create keyboard for next steps
    keyboard = [
        [
            InlineKeyboardButton("Set Welcome Message", callback_data=str(WELCOME_SETUP)),
            InlineKeyboardButton("Set Group Rules", callback_data=str(RULES_SETUP)),
        ],
        [
            InlineKeyboardButton("Finish Setup", callback_data=str(FINISH_SETUP)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{COLORS['primary']} What would you like to set up next?",
        reply_markup=reply_markup
    )
    
    return SELECTING_ACTION


async def finish_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finish the setup conversation."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"{COLORS['success']} Setup complete! The bot is now configured for this group.\n\n"
        f"You can change these settings at any time using the following commands:\n"
        f"- /welcome - Change the welcome message\n"
        f"- /rules - Change the group rules\n"
        f"- /settings - Configure other bot settings"
    )
    
    return ConversationHandler.END


async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the setup conversation."""
    await update.message.reply_text(
        f"{COLORS['neutral']} Setup cancelled. No changes were made to the bot configuration."
    )
    
    return ConversationHandler.END


def get_setup_conversation_handler():
    """Create and return the setup conversation handler."""
    return ConversationHandler(
        entry_points=[CommandHandler('setup', setup_command)],
        states={
            SELECTING_ACTION: [
                CallbackQueryHandler(welcome_setup, pattern=f'^{WELCOME_SETUP}$'),
                CallbackQueryHandler(rules_setup, pattern=f'^{RULES_SETUP}$'),
                CallbackQueryHandler(finish_setup, pattern=f'^{FINISH_SETUP}$'),
            ],
            TYPING_REPLY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_input),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_setup)],
    )


def register_conversation_handlers(application):
    """Register all conversation handlers with the application."""
    # Add the setup conversation handler
    application.add_handler(get_setup_conversation_handler())
