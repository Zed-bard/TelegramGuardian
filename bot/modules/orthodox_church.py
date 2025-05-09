#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Orthodox Church module for Telegram Group Manager Bot.
This module provides specialized functions for Orthodox Church groups,
particularly for Ethiopian Orthodox Church communities.
"""

import logging
import datetime
from typing import Dict, List, Optional, Tuple
from dateutil.easter import easter
from dateutil.relativedelta import relativedelta
import schedule
import time

# Set up logging
logger = logging.getLogger(__name__)

# Ethiopian Orthodox Church special dates and holidays
# These are examples - would need to be filled with accurate data
ETHIOPIAN_ORTHODOX_HOLIDAYS = {
    # Format: "MM-DD": ("Holiday Name", "Description")
    "01-07": ("Ethiopian Christmas (Genna)", "Celebration of the birth of Jesus Christ according to Ethiopian calendar"),
    "01-19": ("Epiphany (Timkat)", "Celebration of the baptism of Jesus Christ"),
    "04-XX": ("Ethiopian Easter (Fasika)", "Easter celebration - date varies yearly"),
    "09-11": ("Ethiopian New Year (Enkutatash)", "Ethiopian New Year celebration"),
    "09-27": ("Meskel", "Finding of the True Cross celebration"),
    # Add more holidays here
}

# Prayer times for different days
PRAYER_TIMES = {
    "daily": [
        ("Morning Prayer", "5:00 AM", "Sunrise prayer (Kidase)"),
        ("Noon Prayer", "12:00 PM", "Midday prayer"),
        ("Evening Prayer", "6:00 PM", "Evening prayer")
    ],
    "sunday": [
        ("Holy Liturgy", "8:00 AM", "Sunday Divine Liturgy"),
        ("Sunday School", "10:30 AM", "Religious education for children and youth")
    ],
    "wednesday": [
        ("Communion Preparation", "7:00 PM", "Prayer and preparation for Holy Communion")
    ],
    "friday": [
        ("Fasting Prayer", "3:00 PM", "Special prayer during Friday fast")
    ]
    # Add more specific prayer times for different days
}

# Recommended readings and scriptures
RECOMMENDED_READINGS = {
    "daily": [
        "Psalms 1-5",
        "Gospel reading of the day"
    ],
    "sunday": [
        "Gospel of the week",
        "Epistles of the week"
    ],
    "major_holidays": [
        "Special liturgical texts",
        "Relevant scripture passages"
    ]
    # Add more recommended readings
}

# Fasting periods in Ethiopian Orthodox tradition
FASTING_PERIODS = [
    {
        "name": "Great Lent (Hudade/Abiy Tsom)",
        "duration": "55 days before Easter",
        "description": "The longest and most important fasting period preceding Easter"
    },
    {
        "name": "Fast of the Apostles (Ye'hawaryat Tsom)",
        "duration": "Varies (from Pentecost until July 12)",
        "description": "Commemorates the apostles' preparation for their missionary work"
    },
    {
        "name": "Fast of the Assumption (Ye'Mariam Tsom)",
        "duration": "August 1-15",
        "description": "Two-week fast preceding the Assumption of Mary"
    },
    {
        "name": "Advent Fast (Ye'Lidet Tsom)",
        "duration": "November 25 - January 6",
        "description": "40-day fast preceding Ethiopian Christmas"
    },
    {
        "name": "Wednesdays and Fridays",
        "duration": "Year-round except for certain feast periods",
        "description": "Regular weekly fasting days"
    }
    # Add more fasting periods
]

def calculate_easter_date(year: int) -> datetime.date:
    """
    Calculate the date of Ethiopian Orthodox Easter (Fasika) for a given year.
    Ethiopian Orthodox Easter is generally 1 week after Western Easter.
    
    Args:
        year: The year to calculate Easter for
        
    Returns:
        datetime.date: The date of Ethiopian Orthodox Easter
    """
    # Get Western Easter date
    western_easter = easter(year)
    
    # Ethiopian Easter is typically one week after Western Easter,
    # but this is a simplification - actual calculation is more complex
    ethiopian_easter = western_easter + datetime.timedelta(days=7)
    
    logger.info(f"Calculated Ethiopian Easter for {year}: {ethiopian_easter}")
    return ethiopian_easter

def get_upcoming_holidays(days_ahead: int = 30) -> List[Dict]:
    """
    Get upcoming Ethiopian Orthodox holidays within the specified number of days.
    
    Args:
        days_ahead: Number of days to look ahead
        
    Returns:
        List[Dict]: List of upcoming holidays with date and description
    """
    today = datetime.date.today()
    end_date = today + datetime.timedelta(days=days_ahead)
    current_year = today.year
    
    upcoming_holidays = []
    
    # Check fixed date holidays
    for date_str, (name, description) in ETHIOPIAN_ORTHODOX_HOLIDAYS.items():
        if date_str == "04-XX":
            # Handle Easter separately since it's date varies
            easter_date = calculate_easter_date(current_year)
            if today <= easter_date <= end_date:
                upcoming_holidays.append({
                    "name": name,
                    "date": easter_date,
                    "description": description
                })
            continue
            
        month, day = map(int, date_str.split("-"))
        holiday_date = datetime.date(current_year, month, day)
        
        # If the holiday has already passed this year, check for next year if within range
        if holiday_date < today:
            holiday_date = datetime.date(current_year + 1, month, day)
            
        if today <= holiday_date <= end_date:
            upcoming_holidays.append({
                "name": name,
                "date": holiday_date,
                "description": description
            })
    
    # Sort by date
    upcoming_holidays.sort(key=lambda x: x["date"])
    
    return upcoming_holidays

def get_daily_prayers(day_of_week: Optional[int] = None) -> List[Dict]:
    """
    Get prayer times for the day.
    
    Args:
        day_of_week: Day of week (0=Monday, 6=Sunday), if None uses today
        
    Returns:
        List[Dict]: List of prayer times with name, time, and description
    """
    if day_of_week is None:
        day_of_week = datetime.datetime.today().weekday()
        
    prayers = []
    
    # Add daily prayers
    for name, time, description in PRAYER_TIMES.get("daily", []):
        prayers.append({
            "name": name,
            "time": time,
            "description": description
        })
    
    # Add day-specific prayers
    day_name = {
        0: "monday",
        1: "tuesday", 
        2: "wednesday",
        3: "thursday",
        4: "friday",
        5: "saturday",
        6: "sunday"
    }.get(day_of_week, "")
    
    for name, time, description in PRAYER_TIMES.get(day_name, []):
        prayers.append({
            "name": name,
            "time": time,
            "description": description
        })
    
    return prayers

def get_daily_readings() -> List[str]:
    """
    Get recommended daily scripture readings.
    
    Returns:
        List[str]: List of recommended readings for today
    """
    today = datetime.datetime.today()
    day_name = ["monday", "tuesday", "wednesday", 
                "thursday", "friday", "saturday", "sunday"][today.weekday()]
    
    # Start with daily readings
    readings = RECOMMENDED_READINGS.get("daily", []).copy()
    
    # Add day-specific readings
    readings.extend(RECOMMENDED_READINGS.get(day_name, []))
    
    # Check if today is a major holiday
    today_str = today.strftime("%m-%d")
    if today_str in ETHIOPIAN_ORTHODOX_HOLIDAYS:
        readings.extend(RECOMMENDED_READINGS.get("major_holidays", []))
    
    return readings

def is_fasting_day() -> Tuple[bool, str]:
    """
    Check if today is a fasting day in the Ethiopian Orthodox tradition.
    
    Returns:
        Tuple[bool, str]: (is_fasting, description)
    """
    today = datetime.datetime.today()
    weekday = today.weekday()
    
    # Wednesday (2) and Friday (4) are regular fasting days
    if weekday == 2:
        return True, "Wednesday Fast: Commemorates the betrayal of Christ"
    elif weekday == 4:
        return True, "Friday Fast: Commemorates the crucifixion of Christ"
    
    # Check for other fasting periods - simplified implementation
    # Would need more complex logic for accurate determination
    
    # For demonstration, just return False
    return False, ""

def setup_prayer_notifications(bot, chat_id):
    """
    Set up scheduled prayer time notifications.
    
    Args:
        bot: The telegram bot instance
        chat_id: The chat ID to send notifications to
    """
    logger.info(f"Setting up prayer notifications for chat {chat_id}")
    
    # Example: Setup morning prayer notification
    def send_morning_prayer():
        message = (
            "🕯️ *Morning Prayer Reminder*\n\n"
            "It is time for morning prayer (Kidase).\n"
            "Today's recommended readings:\n"
        )
        readings = get_daily_readings()
        for reading in readings:
            message += f"- {reading}\n"
        
        try:
            bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            logger.info(f"Sent morning prayer notification to chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send prayer notification: {e}")
    
    # Schedule notifications (example times)
    schedule.every().day.at("05:00").do(send_morning_prayer)
    
    # Would need to run this in a separate thread
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)