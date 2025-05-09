#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Photography and Film module for Telegram Group Manager Bot.
This module provides specialized functions for photography/film businesses
to manage client communications, booking requests, and portfolio sharing.
"""

import logging
import datetime
import re
from typing import Dict, List, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Photography session types
SESSION_TYPES = [
    "portrait",
    "wedding",
    "event",
    "commercial",
    "real_estate",
    "product",
    "documentary",
    "film_production",
    "aerial"
]

# Booking status options
BOOKING_STATUS = [
    "inquiry",
    "pending",
    "confirmed",
    "deposit_paid",
    "completed",
    "canceled"
]

# Equipment categories
EQUIPMENT_CATEGORIES = [
    "camera",
    "lens",
    "lighting",
    "audio",
    "support",  # tripods, gimbals, etc.
    "drone",
    "accessories"
]

class BookingRequest:
    """Class representing a photography/filming booking request"""
    
    def __init__(self, client_name, session_type, date, location, details=None):
        self.client_name = client_name
        self.session_type = session_type
        self.date = date
        self.location = location
        self.details = details
        self.status = "inquiry"
        self.client_contact = None
        self.team_members = []
        self.equipment_needed = []
        self.created_at = datetime.datetime.now()
    
    def to_dict(self):
        """Convert booking request to dictionary for storage"""
        return {
            "client_name": self.client_name,
            "session_type": self.session_type,
            "date": self.date.isoformat() if isinstance(self.date, datetime.datetime) else self.date,
            "location": self.location,
            "details": self.details,
            "status": self.status,
            "client_contact": self.client_contact,
            "team_members": self.team_members,
            "equipment_needed": self.equipment_needed,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create booking request from dictionary"""
        obj = cls(
            client_name=data.get("client_name"),
            session_type=data.get("session_type"),
            date=data.get("date"),
            location=data.get("location"),
            details=data.get("details")
        )
        obj.status = data.get("status", "inquiry")
        obj.client_contact = data.get("client_contact")
        obj.team_members = data.get("team_members", [])
        obj.equipment_needed = data.get("equipment_needed", [])
        if isinstance(data.get("created_at"), str):
            obj.created_at = datetime.datetime.fromisoformat(data.get("created_at"))
        return obj

class Portfolio:
    """Class representing a photography/film portfolio collection"""
    
    def __init__(self, name, category, description=None):
        self.name = name
        self.category = category
        self.description = description
        self.items = []  # List of file_ids or URLs
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self):
        """Convert portfolio to dictionary for storage"""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "items": self.items,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create portfolio from dictionary"""
        obj = cls(
            name=data.get("name"),
            category=data.get("category"),
            description=data.get("description")
        )
        obj.items = data.get("items", [])
        if isinstance(data.get("created_at"), str):
            obj.created_at = datetime.datetime.fromisoformat(data.get("created_at"))
        if isinstance(data.get("updated_at"), str):
            obj.updated_at = datetime.datetime.fromisoformat(data.get("updated_at"))
        return obj
    
    def add_item(self, file_id_or_url):
        """Add an item to the portfolio"""
        self.items.append(file_id_or_url)
        self.updated_at = datetime.datetime.now()

def parse_booking_request(text: str) -> Optional[Dict]:
    """
    Parse booking request from text.
    Format: /book "Client Name" "type:session_type" "date:YYYY-MM-DD HH:MM" "location:Place" ["details:Additional details"]
    
    Args:
        text: The command text to parse
        
    Returns:
        Optional[Dict]: Booking data if valid command, None otherwise
    """
    # Extract client name
    client_match = re.search(r'"([^"]*)"', text)
    if not client_match:
        return None
    
    client_name = client_match.group(1)
    
    # Extract session type
    type_match = re.search(r'type:"?([^"]*)"?', text)
    if not type_match:
        return None
        
    session_type = type_match.group(1)
    if session_type not in SESSION_TYPES:
        session_type = "event"  # Default
    
    # Extract date
    date_match = re.search(r'date:"?([^"]*)"?', text)
    if not date_match:
        return None
        
    date_str = date_match.group(1)
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
    
    # Extract location
    location_match = re.search(r'location:"?([^"]*)"?', text)
    if not location_match:
        return None
        
    location = location_match.group(1)
    
    # Extract optional details
    details = None
    details_match = re.search(r'details:"?([^"]*)"?', text)
    if details_match:
        details = details_match.group(1)
    
    return {
        "client_name": client_name,
        "session_type": session_type,
        "date": date,
        "location": location,
        "details": details
    }

def format_booking_message(booking: Dict) -> str:
    """
    Format booking data into human-readable message.
    
    Args:
        booking: Booking data dictionary
        
    Returns:
        str: Formatted message
    """
    date = booking.get("date")
    if isinstance(date, str):
        try:
            date = datetime.datetime.fromisoformat(date)
        except ValueError:
            pass
    
    if isinstance(date, datetime.datetime):
        date_str = date.strftime("%A, %B %d, %Y at %I:%M %p")
    else:
        date_str = str(date)
    
    message = (
        f"📸 *NEW BOOKING REQUEST*\n\n"
        f"👤 *Client:* {booking.get('client_name')}\n"
        f"📅 *Date:* {date_str}\n"
        f"🗺️ *Location:* {booking.get('location')}\n"
        f"📷 *Session Type:* {booking.get('session_type')}\n"
    )
    
    if booking.get("details"):
        message += f"📝 *Details:* {booking.get('details')}\n"
    
    message += f"\n*Status:* {booking.get('status', 'inquiry')}"
    
    return message

def parse_portfolio_command(text: str) -> Optional[Dict]:
    """
    Parse portfolio command from text.
    Format: /portfolio "Name" "category:category_name" ["description:Description text"]
    
    Args:
        text: The command text to parse
        
    Returns:
        Optional[Dict]: Portfolio data if valid command, None otherwise
    """
    # Extract name
    name_match = re.search(r'"([^"]*)"', text)
    if not name_match:
        return None
    
    name = name_match.group(1)
    
    # Extract category
    category_match = re.search(r'category:"?([^"]*)"?', text)
    if not category_match:
        return None
        
    category = category_match.group(1)
    
    # Extract optional description
    description = None
    desc_match = re.search(r'description:"?([^"]*)"?', text)
    if desc_match:
        description = desc_match.group(1)
    
    return {
        "name": name,
        "category": category,
        "description": description
    }

def format_portfolio_message(portfolio: Dict) -> str:
    """
    Format portfolio data into human-readable message.
    
    Args:
        portfolio: Portfolio data dictionary
        
    Returns:
        str: Formatted message
    """
    message = (
        f"🖼️ *PORTFOLIO: {portfolio.get('name')}*\n\n"
        f"🏷️ *Category:* {portfolio.get('category')}\n"
    )
    
    if portfolio.get("description"):
        message += f"📝 *Description:* {portfolio.get('description')}\n"
    
    items = portfolio.get("items", [])
    message += f"\n*Contains {len(items)} item(s)*"
    
    return message

def get_upcoming_bookings(bookings: List[Dict], days_ahead: int = 14) -> List[Dict]:
    """
    Get list of upcoming bookings within specified days.
    
    Args:
        bookings: List of booking dictionaries
        days_ahead: Number of days to look ahead
        
    Returns:
        List[Dict]: Filtered list of upcoming bookings
    """
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + datetime.timedelta(days=days_ahead)
    
    upcoming = []
    
    for booking in bookings:
        date = booking.get("date")
        
        # Convert string date to datetime if needed
        if isinstance(date, str):
            try:
                date = datetime.datetime.fromisoformat(date)
            except ValueError:
                continue
        
        # Skip if date is not valid
        if not isinstance(date, datetime.datetime):
            continue
            
        # Check if within the specified range and not canceled
        if today <= date <= end_date and booking.get("status") != "canceled":
            upcoming.append(booking)
    
    # Sort by date
    upcoming.sort(key=lambda x: x.get("date"))
    
    return upcoming

def format_upcoming_bookings_message(bookings: List[Dict]) -> str:
    """
    Format a list of upcoming bookings into a human-readable message.
    
    Args:
        bookings: List of booking dictionaries
        
    Returns:
        str: Formatted message
    """
    if not bookings:
        return "📅 *Upcoming Bookings*\n\nNo bookings scheduled for the near future."
    
    message = "📅 *Upcoming Bookings*\n\n"
    
    for i, booking in enumerate(bookings, 1):
        date = booking.get("date")
        
        # Convert string date to datetime if needed
        if isinstance(date, str):
            try:
                date = datetime.datetime.fromisoformat(date)
                date_str = date.strftime("%a, %b %d at %I:%M %p")
            except ValueError:
                date_str = date
        else:
            date_str = date.strftime("%a, %b %d at %I:%M %p") if isinstance(date, datetime.datetime) else str(date)
            
        message += (
            f"{i}. *{booking.get('client_name')}* - {booking.get('session_type')}\n"
            f"   📅 {date_str}\n"
            f"   📍 {booking.get('location')}\n"
            f"   Status: {booking.get('status')}\n\n"
        )
    
    return message

def handle_photo_upload(photo, caption=None, user_id=None):
    """
    Handle photo upload by a user, potentially for portfolio addition.
    
    Args:
        photo: The photo object from Telegram
        caption: Optional caption text
        user_id: The uploader's user ID
        
    Returns:
        Dict: Information about the processed photo
    """
    # Get the largest photo size
    file_id = None
    if isinstance(photo, list) and photo:
        # Sort by file size (width * height)
        photo.sort(key=lambda p: p.width * p.height, reverse=True)
        file_id = photo[0].file_id
    elif hasattr(photo, 'file_id'):
        file_id = photo.file_id
    
    if not file_id:
        return None
    
    # Extract portfolio name from caption if provided
    portfolio_name = None
    if caption and "#portfolio" in caption:
        portfolio_match = re.search(r'#portfolio[_\s]?([a-zA-Z0-9_]+)', caption)
        if portfolio_match:
            portfolio_name = portfolio_match.group(1)
    
    return {
        "file_id": file_id,
        "caption": caption,
        "user_id": user_id,
        "portfolio_name": portfolio_name,
        "timestamp": datetime.datetime.now().isoformat()
    }