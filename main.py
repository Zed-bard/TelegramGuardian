#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import threading
from app import app, db

# This file serves as the main entry point for the Flask application
# The app is defined in app.py

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Initialize database tables
with app.app_context():
    # Import models here to avoid circular imports
    import models  # This imports the models we defined
    
    # Create all tables in the database
    db.create_all()
    logger.info("Database tables created")

# Function to run the bot in polling mode
def run_bot_polling():
    from webhook import get_bot_token, init_bot, start_polling
    
    token = get_bot_token()
    if token:
        try:
            # Initialize the bot
            if init_bot():
                logger.info("Starting bot in polling mode...")
                # Start polling without calling idle() which blocks with signals
                if start_polling():
                    logger.info("Bot polling started successfully")
                else:
                    logger.error("Failed to start polling")
            else:
                logger.error("Failed to initialize bot")
        except Exception as e:
            logger.error(f"Error starting bot in polling mode: {e}")
    else:
        logger.warning("No bot token provided. Bot not started in polling mode.")

# Start polling in a separate thread if enabled
if os.environ.get('BOT_POLLING_ENABLED', 'true').lower() == 'true':
    # Set environment variable
    os.environ['BOT_POLLING_ENABLED'] = 'true'
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot_polling)
    bot_thread.daemon = True  # Thread will die when the main program exits
    bot_thread.start()
    logger.info("Bot polling thread started")

if __name__ == '__main__':
    logger.info("Starting Telegram Group Manager Bot web interface")
    app.run(host='0.0.0.0', port=5000, debug=True)
