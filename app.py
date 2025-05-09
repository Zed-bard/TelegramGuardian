import os
import json
import logging
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Define the base for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Create SQLAlchemy instance
db = SQLAlchemy(model_class=Base)

# Setup Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Configure the database
# The DATABASE_URL may start with 'postgres://' which SQLAlchemy no longer supports
# So we need to replace it with 'postgresql://'
db_url = os.environ.get("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

# Import webhook blueprint after app initialization to avoid circular imports
from webhook import webhook_bp

# Register the webhook blueprint
app.register_blueprint(webhook_bp)

# Bot features and settings
features = [
    {
        "name": "Welcome New Members",
        "description": "Automatically greet new users joining your groups",
        "icon": "👋"
    },
    {
        "name": "Permission Management",
        "description": "Manage user permissions with admin, moderator, and regular user levels",
        "icon": "🔒"
    },
    {
        "name": "Content Moderation",
        "description": "Automatically detect and filter inappropriate content",
        "icon": "🛡️"
    },
    {
        "name": "Group Rules",
        "description": "Set and display group rules for members",
        "icon": "📝"
    },
    {
        "name": "User Warnings",
        "description": "Issue warnings to users who violate group guidelines",
        "icon": "⚠️"
    },
    {
        "name": "Statistics Tracking",
        "description": "Track group activity and user engagement metrics",
        "icon": "📊"
    }
]

commands = [
    {"cmd": "/start", "description": "Initialize the bot and get a greeting message"},
    {"cmd": "/help", "description": "Display help with all available commands"},
    {"cmd": "/welcome", "description": "Set a custom welcome message for new members"},
    {"cmd": "/rules", "description": "View or set group rules"},
    {"cmd": "/promote", "description": "Promote a user to a higher permission level"},
    {"cmd": "/demote", "description": "Demote a user to a lower permission level"},
    {"cmd": "/warn", "description": "Warn a user about inappropriate behavior"},
    {"cmd": "/ban", "description": "Ban a user from the group"},
    {"cmd": "/unban", "description": "Unban a previously banned user"},
    {"cmd": "/mute", "description": "Restrict a user from sending messages"},
    {"cmd": "/unmute", "description": "Allow a muted user to send messages again"},
    {"cmd": "/stats", "description": "View group statistics"},
    {"cmd": "/settings", "description": "Configure bot settings for this group"}
]

@app.route('/')
def index():
    """Home page showing bot information."""
    return render_template('index.html', 
                          features=features, 
                          commands=commands,
                          bot_name="Telegram Group Manager Bot")

@app.route('/api/status')
def status():
    """API endpoint for bot status."""
    return jsonify({
        'status': 'running',
        'app': 'Telegram Group Manager Bot',
        'description': 'A bot for managing group communications, user permissions, and automated interactions.',
        'features_count': len(features),
        'commands_count': len(commands)
    })

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup page for configuring the bot."""
    if request.method == 'POST':
        token = request.form.get('token')
        if token:
            try:
                # Validate the token format
                if not token.strip() or ':' not in token:
                    flash('Invalid token format. Please provide a valid Telegram bot token.')
                    return render_template('setup.html', error='Invalid token format')
                
                # Store the token in environment variable
                os.environ['TELEGRAM_BOT_TOKEN'] = token
                
                # Update the config file
                config_path = 'config.json'
                config = {}
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                    except Exception as e:
                        logger.error(f"Error loading config: {e}")
                
                # Save token in config
                config['bot_token'] = token
                
                # Get bot information from Telegram API
                try:
                    import telegram
                    bot = telegram.Bot(token=token)
                    bot_info = bot.get_me()
                    logger.info(f"Connected to bot: {bot_info.username}")
                    
                    # Save bot username in config
                    config['bot_username'] = bot_info.username
                    config['bot_name'] = bot_info.first_name
                    
                except Exception as e:
                    logger.error(f"Error connecting to Telegram API: {e}")
                    flash('Could not connect to Telegram API with the provided token. Please check your token.')
                    return render_template('setup.html', error='Invalid token')
                
                # Save config to file
                try:
                    with open(config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    logger.info("Bot token and info saved successfully")
                    
                    # Reinitialize the bot
                    from webhook import init_bot
                    if init_bot():
                        logger.info("Bot reinitialized successfully")
                    else:
                        logger.error("Failed to reinitialize bot")
                        flash('Failed to initialize the bot. Please try again.')
                        return render_template('setup.html', error='Initialization failed')
                except Exception as e:
                    logger.error(f"Error saving config: {e}")
                    flash('An error occurred while saving configuration. Please try again.')
                    return render_template('setup.html', error='Config save error')
                
                return redirect(url_for('setup_success'))
            except Exception as e:
                logger.error(f"Unexpected error during setup: {e}")
                flash('An unexpected error occurred. Please try again.')
                return render_template('setup.html', error='Unexpected error')
        else:
            flash('Please provide a valid Telegram bot token.')
            return render_template('setup.html', error='No token provided')
            
    return render_template('setup.html')

@app.route('/setup/success')
def setup_success():
    """Page shown after successful setup."""
    return render_template('setup_success.html')

@app.route('/docs')
def docs():
    """Documentation page."""
    return render_template('docs.html', commands=commands)

# Create templates directory
os.makedirs('templates', exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)