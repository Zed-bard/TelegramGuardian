"""
Database utility functions for the Telegram Group Manager Bot.
This module provides functions for database operations.
"""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db
from models import User, Group, Member, GroupSetting, LogEntry


def get_or_create_user(telegram_id, username=None, first_name=None, last_name=None, language_code=None):
    """
    Get an existing user or create a new one.
    
    Args:
        telegram_id: The user's Telegram ID
        username: The user's username (optional)
        first_name: The user's first name (optional)
        last_name: The user's last name (optional)
        language_code: The user's language code (optional)
        
    Returns:
        User: The user object
    """
    try:
        user = User.query.filter_by(telegram_id=str(telegram_id)).first()
        
        if not user:
            user = User(
                telegram_id=str(telegram_id),
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code
            )
            db.session.add(user)
            db.session.commit()
        elif any([
            username and user.username != username,
            first_name and user.first_name != first_name,
            last_name and user.last_name != last_name,
            language_code and user.language_code != language_code
        ]):
            # Update user info if it has changed
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if language_code:
                user.language_code = language_code
                
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_or_create_group(telegram_id, title, description=None):
    """
    Get an existing group or create a new one.
    
    Args:
        telegram_id: The group's Telegram ID
        title: The group's title
        description: The group's description (optional)
        
    Returns:
        Group: The group object
    """
    try:
        group = Group.query.filter_by(telegram_id=str(telegram_id)).first()
        
        if not group:
            group = Group(
                telegram_id=str(telegram_id),
                title=title,
                description=description
            )
            db.session.add(group)
            db.session.commit()
        elif any([
            group.title != title,
            description and group.description != description
        ]):
            # Update group info if it has changed
            group.title = title
            if description:
                group.description = description
                
            group.updated_at = datetime.utcnow()
            db.session.commit()
            
        return group
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_or_create_member(user_id, group_id, permission_level=0):
    """
    Get an existing member or create a new one.
    
    Args:
        user_id: The user's ID
        group_id: The group's ID
        permission_level: The member's permission level (default: 0)
        
    Returns:
        Member: The member object
    """
    try:
        # First get user and group objects
        user = User.query.get(user_id)
        group = Group.query.get(group_id)
        
        if not user or not group:
            return None
            
        member = Member.query.filter_by(user_id=user_id, group_id=group_id).first()
        
        if not member:
            member = Member(
                user_id=user_id,
                group_id=group_id,
                permission_level=permission_level
            )
            db.session.add(member)
            db.session.commit()
            
        return member
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_group_setting(group_id, key, default=None):
    """
    Get a group setting.
    
    Args:
        group_id: The group's ID
        key: The setting key
        default: The default value to return if the setting doesn't exist
        
    Returns:
        The setting value or the default
    """
    try:
        setting = GroupSetting.query.filter_by(group_id=group_id, key=key).first()
        
        if setting:
            return setting.value
        return default
    except SQLAlchemyError:
        return default


def set_group_setting(group_id, key, value):
    """
    Set a group setting.
    
    Args:
        group_id: The group's ID
        key: The setting key
        value: The setting value
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        setting = GroupSetting.query.filter_by(group_id=group_id, key=key).first()
        
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = GroupSetting(
                group_id=group_id,
                key=key,
                value=value
            )
            db.session.add(setting)
            
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        return False


def log_event(event_type, description=None, group_id=None, user_id=None, meta_data=None):
    """
    Log an event.
    
    Args:
        event_type: The type of event
        description: A description of the event (optional)
        group_id: The group's ID (optional)
        user_id: The user's ID (optional)
        meta_data: Additional metadata (optional)
        
    Returns:
        LogEntry: The log entry object, or None if an error occurred
    """
    try:
        log_entry = LogEntry(
            event_type=event_type,
            description=description,
            group_id=group_id,
            user_id=user_id,
            meta_data=meta_data
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return log_entry
    except SQLAlchemyError as e:
        db.session.rollback()
        return None


def update_member_permission(user_id, group_id, permission_level):
    """
    Update a member's permission level.
    
    Args:
        user_id: The user's ID
        group_id: The group's ID
        permission_level: The new permission level
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        member = Member.query.filter_by(user_id=user_id, group_id=group_id).first()
        
        if member:
            member.permission_level = permission_level
            member.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        return False


def get_user_by_telegram_id(telegram_id):
    """
    Get a user by their Telegram ID.
    
    Args:
        telegram_id: The user's Telegram ID
        
    Returns:
        User: The user object, or None if not found
    """
    return User.query.filter_by(telegram_id=str(telegram_id)).first()


def get_group_by_telegram_id(telegram_id):
    """
    Get a group by its Telegram ID.
    
    Args:
        telegram_id: The group's Telegram ID
        
    Returns:
        Group: The group object, or None if not found
    """
    return Group.query.filter_by(telegram_id=str(telegram_id)).first()


def get_member_permission(user_id, group_id):
    """
    Get a member's permission level.
    
    Args:
        user_id: The user's ID
        group_id: The group's ID
        
    Returns:
        int: The permission level, or 0 if the member doesn't exist
    """
    member = Member.query.filter_by(user_id=user_id, group_id=group_id).first()
    
    if member:
        return member.permission_level
    return 0


def increment_user_warning(user_id, group_id):
    """
    Increment a user's warning count.
    
    Args:
        user_id: The user's ID
        group_id: The group's ID
        
    Returns:
        int: The new warning count, or None if an error occurred
    """
    try:
        member = Member.query.filter_by(user_id=user_id, group_id=group_id).first()
        
        if member:
            member.warnings += 1
            member.updated_at = datetime.utcnow()
            db.session.commit()
            return member.warnings
        return None
    except SQLAlchemyError as e:
        db.session.rollback()
        return None


def reset_user_warnings(user_id, group_id):
    """
    Reset a user's warning count.
    
    Args:
        user_id: The user's ID
        group_id: The group's ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        member = Member.query.filter_by(user_id=user_id, group_id=group_id).first()
        
        if member:
            member.warnings = 0
            member.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        db.session.rollback()
        return False


def get_group_stats(group_id):
    """
    Get statistics for a group.
    
    Args:
        group_id: The group's ID
        
    Returns:
        dict: The group statistics
    """
    try:
        # Total members
        total_members = Member.query.filter_by(group_id=group_id).count()
        
        # Members by permission level
        admin_count = Member.query.filter_by(group_id=group_id, permission_level=100).count()
        mod_count = Member.query.filter_by(group_id=group_id, permission_level=50).count()
        trusted_count = Member.query.filter_by(group_id=group_id, permission_level=10).count()
        restricted_count = Member.query.filter_by(group_id=group_id, permission_level=-10).count()
        banned_count = Member.query.filter_by(group_id=group_id, permission_level=-100).count()
        
        return {
            'total_members': total_members,
            'admins': admin_count,
            'moderators': mod_count,
            'trusted': trusted_count,
            'restricted': restricted_count,
            'banned': banned_count,
            'regular': total_members - (admin_count + mod_count + trusted_count + restricted_count + banned_count)
        }
    except SQLAlchemyError:
        return {
            'total_members': 0,
            'admins': 0,
            'moderators': 0,
            'trusted': 0,
            'restricted': 0,
            'banned': 0,
            'regular': 0
        }