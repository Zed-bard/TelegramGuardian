#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Specialized command handlers for the Telegram Group Manager Bot.
This module contains handlers for specialized domain commands like
Orthodox church features, educational institution features, and
photography/film business features.
"""

import logging
import datetime
from typing import Dict, List, Optional, Tuple
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from bot.config import COLORS
from bot.storage.data import get_group_data, save_group_data
from bot.modules import orthodox_church, education, photography, ai_assistant

# Set up logging
logger = logging.getLogger(__name__)

# Dictionary to store module specific data
MODULE_DATA = {
    "church": {},    # Orthodox Church module data
    "education": {}, # Education module data
    "photography": {}  # Photography module data
}

# Group configurations
GROUP_CONFIGS = {}  # chat_id -> {"active_modules": [...], "settings": {...}}

#
# Orthodox Church handlers
#
def prayer_times_command(update: Update, context: CallbackContext) -> None:
    """Show prayer times for today."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /prayer_times command from user: {user.id} in chat: {chat.id}")
        
        prayers = orthodox_church.get_daily_prayers()
        
        message = "🕯️ *Prayer Times for Today*\n\n"
        
        for prayer in prayers:
            message += (
                f"*{prayer['name']}* - {prayer['time']}\n"
                f"{prayer['description']}\n\n"
            )
        
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Sent prayer times to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /prayer_times command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error getting the prayer times. Please try again later.")
        except:
            pass

def readings_command(update: Update, context: CallbackContext) -> None:
    """Show recommended readings for today."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /readings command from user: {user.id} in chat: {chat.id}")
        
        readings = orthodox_church.get_daily_readings()
        
        message = "📖 *Recommended Readings for Today*\n\n"
        
        for reading in readings:
            message += f"- {reading}\n"
        
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Sent daily readings to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /readings command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error getting the daily readings. Please try again later.")
        except:
            pass

def holidays_command(update: Update, context: CallbackContext) -> None:
    """Show upcoming Orthodox holidays."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /holidays command from user: {user.id} in chat: {chat.id}")
        
        # Default to 30 days, or use provided argument
        days_ahead = 30
        if context.args and context.args[0].isdigit():
            days_ahead = min(365, int(context.args[0]))  # Limit to 1 year
        
        holidays = orthodox_church.get_upcoming_holidays(days_ahead)
        
        if not holidays:
            update.message.reply_text(
                f"No Orthodox holidays in the next {days_ahead} days.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        message = f"🎄 *Upcoming Orthodox Holidays (Next {days_ahead} days)*\n\n"
        
        for holiday in holidays:
            date_str = holiday['date'].strftime("%A, %B %d, %Y")
            message += (
                f"*{holiday['name']}*\n"
                f"📅 {date_str}\n"
                f"{holiday['description']}\n\n"
            )
        
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Sent upcoming holidays to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /holidays command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error getting the upcoming holidays. Please try again later.")
        except:
            pass

def fasting_command(update: Update, context: CallbackContext) -> None:
    """Check if today is a fasting day."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /fasting command from user: {user.id} in chat: {chat.id}")
        
        is_fasting, description = orthodox_church.is_fasting_day()
        
        if is_fasting:
            message = (
                "✝️ *Today is a Fasting Day*\n\n"
                f"{description}\n\n"
                "Remember to abstain from animal products and focus on prayer."
            )
        else:
            message = (
                "✝️ *Today is Not a Fasting Day*\n\n"
                "Regular dietary observances apply."
            )
        
        # Add information about fasting periods
        message += "\n\n*Major Fasting Periods:*\n"
        for period in orthodox_church.FASTING_PERIODS[:3]:  # Show first 3
            message += f"- *{period['name']}*: {period['duration']}\n"
        
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Sent fasting information to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /fasting command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error checking fasting information. Please try again later.")
        except:
            pass

#
# Education handlers
#
def assignment_command(update: Update, context: CallbackContext) -> None:
    """Create or view assignments."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /assignment command from user: {user.id} in chat: {chat.id}")
        
        # Get group data and ensure assignments list exists
        group_data = get_group_data(chat.id)
        if 'assignments' not in group_data:
            group_data['assignments'] = []
        
        # If no arguments, show upcoming assignments
        if not context.args:
            assignments = group_data['assignments']
            upcoming = education.get_upcoming_assignments(assignments)
            
            message = education.format_upcoming_assignments_message(upcoming)
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Sent assignments list to user {user.id}")
            return
        
        # Parse the assignment command
        full_text = ' '.join(context.args)
        assignment_data = education.parse_assignment_command(full_text)
        
        if not assignment_data:
            update.message.reply_text(
                "📝 *Assignment Format Error*\n\n"
                "Please use the format:\n"
                '/assignment "Title" "Description" "YYYY-MM-DD" [#class_id] [grade:level]\n\n'
                "Example:\n"
                '/assignment "Math Homework" "Complete exercises 1-10" "2025-05-20" #math grade:10',
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Add the user ID as assigned_by
        assignment_data['assigned_by'] = user.id
        
        # Convert to Assignment object and back to dict for storage
        assignment = education.Assignment(**assignment_data)
        assignment_dict = assignment.to_dict()
        
        # Add to group data
        group_data['assignments'].append(assignment_dict)
        save_group_data(chat.id, group_data)
        
        # Reply with formatted assignment
        message = education.format_assignment_message(assignment_dict)
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Created new assignment from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /assignment command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your assignment. Please try again later.")
        except:
            pass

def question_command(update: Update, context: CallbackContext) -> None:
    """Create or view educational questions."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /question command from user: {user.id} in chat: {chat.id}")
        
        # Get group data and ensure questions list exists
        group_data = get_group_data(chat.id)
        if 'questions' not in group_data:
            group_data['questions'] = []
        
        # If no arguments, show info about asking questions
        if not context.args:
            message = (
                "❓ *Educational Questions*\n\n"
                "To ask a question, use the format:\n"
                '/question "Your question here" [type:question_type] [options:"A|B|C"] [answer:correct_answer]\n\n'
                "Question types:\n"
                "- multiple_choice\n"
                "- essay\n"
                "- short_answer (default)\n"
                "- file_upload\n\n"
                "Example:\n"
                '/question "What is the capital of Ethiopia?" type:multiple_choice options:"Addis Ababa|Lagos|Nairobi" answer:A'
            )
            update.message.reply_text(
                message, 
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Parse the question command
        full_text = ' '.join(context.args)
        question_data = education.parse_question_command(full_text)
        
        if not question_data:
            update.message.reply_text(
                "❓ *Question Format Error*\n\n"
                "Please use the format:\n"
                '/question "Your question here"',
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Add the user ID as asked_by
        question_data['asked_by'] = user.id
        
        # Convert to Question object and back to dict for storage
        question = education.Question(**question_data)
        question_dict = question.to_dict()
        
        # Add to group data
        group_data['questions'].append(question_dict)
        save_group_data(chat.id, group_data)
        
        # Reply with formatted question
        message = education.format_question_message(question_dict)
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Created new question from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /question command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your question. Please try again later.")
        except:
            pass

#
# Photography/Film handlers
#
def book_command(update: Update, context: CallbackContext) -> None:
    """Create or view booking requests."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /book command from user: {user.id} in chat: {chat.id}")
        
        # Get group data and ensure bookings list exists
        group_data = get_group_data(chat.id)
        if 'bookings' not in group_data:
            group_data['bookings'] = []
        
        # If no arguments, show upcoming bookings
        if not context.args:
            bookings = group_data['bookings']
            upcoming = photography.get_upcoming_bookings(bookings)
            
            message = photography.format_upcoming_bookings_message(upcoming)
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Sent bookings list to user {user.id}")
            return
        
        # Parse the booking command
        full_text = ' '.join(context.args)
        booking_data = photography.parse_booking_request(full_text)
        
        if not booking_data:
            update.message.reply_text(
                "📸 *Booking Format Error*\n\n"
                "Please use the format:\n"
                '/book "Client Name" type:"session_type" date:"YYYY-MM-DD HH:MM" location:"Place" [details:"Additional details"]\n\n'
                "Session types: portrait, wedding, event, commercial, real_estate, product, documentary, film_production, aerial\n\n"
                "Example:\n"
                '/book "John Smith" type:"wedding" date:"2025-06-15 14:00" location:"St. Mary Church" details:"Ceremony and reception"',
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Convert to BookingRequest object and back to dict for storage
        booking = photography.BookingRequest(**booking_data)
        booking_dict = booking.to_dict()
        
        # Add to group data
        group_data['bookings'].append(booking_dict)
        save_group_data(chat.id, group_data)
        
        # Reply with formatted booking
        message = photography.format_booking_message(booking_dict)
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Created new booking from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /book command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your booking. Please try again later.")
        except:
            pass

def portfolio_command(update: Update, context: CallbackContext) -> None:
    """Create or view photography portfolios."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /portfolio command from user: {user.id} in chat: {chat.id}")
        
        # Get group data and ensure portfolios dict exists
        group_data = get_group_data(chat.id)
        if 'portfolios' not in group_data:
            group_data['portfolios'] = {}
        
        # If no arguments, show list of portfolios
        if not context.args:
            portfolios = group_data['portfolios']
            
            if not portfolios:
                message = (
                    "🖼️ *Photography Portfolios*\n\n"
                    "No portfolios created yet.\n\n"
                    "To create a portfolio, use:\n"
                    '/portfolio "Name" category:"category_name" [description:"Description text"]'
                )
            else:
                message = "🖼️ *Photography Portfolios*\n\n"
                for name, portfolio in portfolios.items():
                    item_count = len(portfolio.get('items', []))
                    message += (
                        f"*{name}* - {portfolio.get('category')}\n"
                        f"Contains {item_count} item(s)\n\n"
                    )
                message += (
                    "To view a portfolio, use:\n"
                    "/portfolio_view [name]\n\n"
                    "To add photos to a portfolio, send a photo with caption: #portfolio_[name]"
                )
            
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Sent portfolios list to user {user.id}")
            return
        
        # Parse the portfolio command
        full_text = ' '.join(context.args)
        portfolio_data = photography.parse_portfolio_command(full_text)
        
        if not portfolio_data:
            update.message.reply_text(
                "🖼️ *Portfolio Format Error*\n\n"
                "Please use the format:\n"
                '/portfolio "Name" category:"category_name" [description:"Description text"]',
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Convert to Portfolio object and back to dict for storage
        portfolio = photography.Portfolio(**portfolio_data)
        portfolio_dict = portfolio.to_dict()
        
        # Add to group data
        group_data['portfolios'][portfolio_data['name']] = portfolio_dict
        save_group_data(chat.id, group_data)
        
        # Reply with formatted portfolio
        message = photography.format_portfolio_message(portfolio_dict)
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Created new portfolio from user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /portfolio command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your portfolio request. Please try again later.")
        except:
            pass

#
# AI Assistant handlers
#
def ai_command(update: Update, context: CallbackContext) -> None:
    """Process AI assistant commands and questions."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /ai command from user: {user.id} in chat: {chat.id}")
        
        # If no arguments, show AI context options
        if not context.args:
            message = ai_assistant.format_ai_context_message()
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info(f"Sent AI context options to user {user.id}")
            return
        
        # Process user's question
        user_message = ' '.join(context.args)
        user_id = user.id
        
        # Generate response based on the message
        response = ai_assistant.generate_ai_response(user_id, user_message)
        
        # Send the AI response
        update.message.reply_text(
            response,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Sent AI response to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /ai command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your AI request. Please try again later.")
        except:
            pass

def ai_context_command(update: Update, context: CallbackContext) -> None:
    """Set AI conversation context."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        command_parts = update.message.text.split('_', 1)
        
        # Extract context from command (e.g., /ai_orthodox_church -> orthodox_church)
        if len(command_parts) < 2:
            update.message.reply_text(
                "Please specify a context: /ai_[context_name]",
                parse_mode=ParseMode.MARKDOWN
            )
            return
            
        context_name = command_parts[1]
        logger.info(f"Setting AI context to {context_name} for user: {user.id}")
        
        # Set the context
        result = ai_assistant.set_conversation_context(user.id, context_name)
        
        if result:
            # Get example questions for this context
            examples = ai_assistant.get_example_questions(context_name)
            example_str = "\n".join([f"- {ex}" for ex in examples[:3]]) if examples else "No examples available"
            
            update.message.reply_text(
                f"🤖 AI context set to: *{context_name}*\n\n"
                f"Example questions you can ask:\n{example_str}\n\n"
                f"Ask a question with /ai [your question]",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            available_contexts = ", ".join(ai_assistant.get_available_contexts())
            update.message.reply_text(
                f"Invalid context: {context_name}\n\n"
                f"Available contexts: {available_contexts}",
                parse_mode=ParseMode.MARKDOWN
            )
        
    except Exception as e:
        logger.error(f"Error handling AI context command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error setting the AI context. Please try again later.")
        except:
            pass

def ai_reset_command(update: Update, context: CallbackContext) -> None:
    """Reset AI conversation history."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Resetting AI conversation for user: {user.id}")
        
        # Reset the conversation
        result = ai_assistant.reset_conversation(user.id)
        
        if result:
            update.message.reply_text(
                "🤖 Your AI conversation history has been reset. You're starting with a fresh conversation.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.message.reply_text(
                "Sorry, there was an error resetting your conversation.",
                parse_mode=ParseMode.MARKDOWN
            )
        
    except Exception as e:
        logger.error(f"Error handling AI reset command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error processing your request. Please try again later.")
        except:
            pass

def activate_module_command(update: Update, context: CallbackContext) -> None:
    """Activate specific modules for a group."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /activate_module command from user: {user.id} in chat: {chat.id}")
        
        # Only allow in group chats
        if chat.type == 'private':
            update.message.reply_text(
                "This command can only be used in group chats.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        available_modules = ["orthodox_church", "education", "photography", "ai_assistant"]
        
        # If no arguments, show available modules
        if not context.args:
            # Initialize group config if not exists
            if chat.id not in GROUP_CONFIGS:
                GROUP_CONFIGS[chat.id] = {
                    "active_modules": [],
                    "settings": {}
                }
            
            active_modules = GROUP_CONFIGS[chat.id]["active_modules"]
            
            message = (
                "📋 *Available Specialized Modules*\n\n"
                "To activate a module, use: /activate_module [module_name]\n\n"
                "Available modules:\n"
            )
            
            for module in available_modules:
                status = "✅ Active" if module in active_modules else "❌ Inactive"
                message += f"- *{module}*: {status}\n"
            
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get the module to activate
        module_name = context.args[0].lower()
        
        if module_name not in available_modules:
            update.message.reply_text(
                f"Unknown module: {module_name}\n\n"
                f"Available modules: {', '.join(available_modules)}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Initialize group config if not exists
        if chat.id not in GROUP_CONFIGS:
            GROUP_CONFIGS[chat.id] = {
                "active_modules": [],
                "settings": {}
            }
        
        # Activate the module
        if module_name not in GROUP_CONFIGS[chat.id]["active_modules"]:
            GROUP_CONFIGS[chat.id]["active_modules"].append(module_name)
        
        update.message.reply_text(
            f"✅ Module *{module_name}* is now active!\n\n"
            f"Use /module_help {module_name} to see available commands.",
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Activated module {module_name} for chat {chat.id}")
        
    except Exception as e:
        logger.error(f"Error handling /activate_module command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error activating the module. Please try again later.")
        except:
            pass

def module_help_command(update: Update, context: CallbackContext) -> None:
    """Show help for specific modules."""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        logger.info(f"Received /module_help command from user: {user.id} in chat: {chat.id}")
        
        # Module specific help messages
        help_messages = {
            "orthodox_church": (
                "✝️ *Orthodox Church Module Help*\n\n"
                "Available commands:\n"
                "/prayer_times - Show prayer times for today\n"
                "/readings - Show recommended scripture readings\n"
                "/holidays [days] - Show upcoming holidays\n"
                "/fasting - Check if today is a fasting day\n"
            ),
            "education": (
                "📚 *Education Module Help*\n\n"
                "Available commands:\n"
                "/assignment - View or create assignments\n"
                "/question - Ask or create educational questions\n"
            ),
            "photography": (
                "📸 *Photography Module Help*\n\n"
                "Available commands:\n"
                "/book - View or create booking requests\n"
                "/portfolio - View or create photography portfolios\n"
            ),
            "ai_assistant": (
                "🤖 *AI Assistant Module Help*\n\n"
                "Available commands:\n"
                "/ai [question] - Ask the AI a question\n"
                "/ai_[context_name] - Set the AI conversation context\n"
                "/ai_reset - Reset your conversation history\n\n"
                "Available contexts: orthodox_church, education, photography, general"
            )
        }
        
        # If no arguments, show all module help
        if not context.args:
            message = "📋 *Module Help*\n\nSpecify a module to see help: /module_help [module_name]\n\n"
            message += "Available modules:\n"
            
            for module in help_messages.keys():
                message += f"- {module}\n"
                
            update.message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get the module help
        module_name = context.args[0].lower()
        
        if module_name not in help_messages:
            update.message.reply_text(
                f"Unknown module: {module_name}\n\n"
                f"Available modules: {', '.join(help_messages.keys())}",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Show the module help
        update.message.reply_text(
            help_messages[module_name],
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info(f"Sent help for module {module_name} to user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling /module_help command: {e}")
        try:
            update.message.reply_text("Sorry, there was an error showing module help. Please try again later.")
        except:
            pass

def register_specialized_handlers(application):
    """Register all specialized command handlers with the application."""
    # Orthodox Church handlers
    application.add_handler(CommandHandler("prayer_times", prayer_times_command))
    application.add_handler(CommandHandler("readings", readings_command))
    application.add_handler(CommandHandler("holidays", holidays_command))
    application.add_handler(CommandHandler("fasting", fasting_command))
    
    # Education handlers
    application.add_handler(CommandHandler("assignment", assignment_command))
    application.add_handler(CommandHandler("question", question_command))
    
    # Photography handlers
    application.add_handler(CommandHandler("book", book_command))
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    
    # AI Assistant handlers
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("ai_reset", ai_reset_command))
    
    # Handle AI context commands like /ai_orthodox_church, /ai_education, etc.
    for context in ai_assistant.get_available_contexts():
        application.add_handler(CommandHandler(f"ai_{context}", ai_context_command))
    
    # Module management
    application.add_handler(CommandHandler("activate_module", activate_module_command))
    application.add_handler(CommandHandler("module_help", module_help_command))
    
    # Log registration
    logger.info("Specialized command handlers registered")