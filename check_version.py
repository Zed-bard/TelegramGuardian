import pkg_resources

# Get version of python-telegram-bot
try:
    version = pkg_resources.get_distribution("python-telegram-bot").version
    print(f"python-telegram-bot version: {version}")
except pkg_resources.DistributionNotFound:
    print("python-telegram-bot is not installed")

# Check if telegram.Chat is importable
try:
    from telegram import Chat
    print("telegram.Chat can be imported")
except ImportError as e:
    print(f"Cannot import telegram.Chat: {e}")

# Check what's available in telegram package
try:
    import telegram
    print("\nAvailable in telegram package:")
    for item in dir(telegram):
        if not item.startswith('_'):
            print(f"- {item}")
except ImportError as e:
    print(f"Cannot import telegram: {e}")