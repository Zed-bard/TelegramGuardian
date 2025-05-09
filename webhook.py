#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from flask import Blueprint, request, jsonify
from telegram import Update
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, 
    CallbackQueryHandler, Dispatcher
)

# Create a Blueprint for webhook routes
webhook_bp = Blueprint('webhook', __name__)

# Set up logging
logger = logging.getLogger(__name__)

# Create the bot updater and dispatcher
updater = None
dispatcher = None

# Get bot token from environment or config file
def get_bot_token():
    # First try environment variable
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if token:
        return token
    
    # Then try config file
    config_path = 'config.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                token = config.get('bot_token')
                if token:
                    return token
        except Exception as e:
            logger.error(f"Error loading token from config file: {e}")
    
    # Finally, try the bot.config module
    try:
        from bot.config import BOT_TOKEN
        if BOT_TOKEN:
            return BOT_TOKEN
    except Exception as e:
        logger.error(f"Error importing BOT_TOKEN from config: {e}")
    
    return None

# Initialize the bot if a token is provided
def init_bot():
    global updater, dispatcher
    
    token = get_bot_token()
    
    if token:
        try:
            updater = Updater(token=token, use_context=True)
            dispatcher = updater.dispatcher
            
            # Import handlers here to avoid circular imports
            from bot.handlers.command_handlers_new import register_command_handlers
            from bot.handlers.message_handlers_new import register_message_handlers
            
            # Register handlers
            register_command_handlers(dispatcher)
            register_message_handlers(dispatcher)
            
            logger.info("Bot initialized successfully with provided token")
            return True
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            return False
    else:
        logger.warning("No bot token provided. Bot not initialized.")
        return False

# Initialize the bot when the module is loaded
bot_initialized = init_bot()

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests from Telegram."""
    if not bot_initialized:
        return jsonify({'status': 'error', 'message': 'Bot not initialized. No token provided.'}), 500
    
    if request.method == 'POST':
        try:
            # Parse the update
            update = Update.de_json(request.get_json(force=True), updater.bot)
            
            # Process the update
            dispatcher.process_update(update)
            
            return jsonify({'status': 'ok'})
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    return jsonify({'status': 'error', 'message': 'Method not allowed'}), 405


@webhook_bp.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set up the webhook for Telegram."""
    if not bot_initialized:
        return jsonify({'status': 'error', 'message': 'Bot not initialized. No token provided.'}), 500
    
    webhook_url = request.args.get('url')
    
    if not webhook_url:
        return jsonify({'status': 'error', 'message': 'No URL provided'}), 400
    
    try:
        # Set the webhook
        updater.bot.set_webhook(webhook_url)
        return jsonify({'status': 'ok', 'message': f'Webhook set to {webhook_url}'})
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@webhook_bp.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    """Remove the webhook."""
    if not bot_initialized:
        return jsonify({'status': 'error', 'message': 'Bot not initialized. No token provided.'}), 500
    
    try:
        # Remove the webhook
        updater.bot.delete_webhook()
        return jsonify({'status': 'ok', 'message': 'Webhook removed'})
    except Exception as e:
        logger.error(f"Error removing webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Function to start the bot in polling mode
def start_polling():
    """Start the bot in polling mode."""
    global updater
    
    if not updater:
        success = init_bot()
        if not success:
            logger.error("Failed to initialize bot for polling")
            return False
    
    try:
        logger.info("Bot is running in polling mode... Press Ctrl+C to stop.")
        updater.start_polling()
        logger.info("Bot polling started successfully!")
        return True
    except Exception as e:
        logger.error(f"Error starting polling: {e}")
        return False

# Start the bot in polling mode if called directly
if __name__ == '__main__':
    if init_bot():
        # Start the Bot in polling mode
        updater.start_polling()
        logger.info("Bot is running in polling mode... Press Ctrl+C to stop.")
        updater.idle()
