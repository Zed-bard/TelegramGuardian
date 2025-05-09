from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app import db

class Group(db.Model):
    """
    Model for Telegram groups/chats managed by the bot.
    """
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    welcome_message = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)
    moderation_enabled = Column(Boolean, default=True)
    auto_delete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    members = relationship("Member", back_populates="group", cascade="all, delete-orphan")
    settings = relationship("GroupSetting", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Group(id={self.id}, title='{self.title}')>"


class User(db.Model):
    """
    Model for Telegram users interacting with the bot.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    language_code = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = relationship("Member", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Member(db.Model):
    """
    Model for the membership of a user in a group.
    This represents the many-to-many relationship between users and groups
    with additional membership attributes.
    """
    __tablename__ = 'members'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    permission_level = Column(Integer, default=0)  # 0: regular user, -10: restricted, -100: banned, 10: trusted, 50: moderator, 100: admin, 1000: owner
    warnings = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="memberships")
    group = relationship("Group", back_populates="members")
    
    def __repr__(self):
        return f"<Member(user_id={self.user_id}, group_id={self.group_id}, permission_level={self.permission_level})>"


class GroupSetting(db.Model):
    """
    Model for group-specific bot settings.
    """
    __tablename__ = 'group_settings'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group = relationship("Group", back_populates="settings")
    
    def __repr__(self):
        return f"<GroupSetting(group_id={self.group_id}, key='{self.key}')>"


class LogEntry(db.Model):
    """
    Model for logging bot activities and events.
    """
    __tablename__ = 'log_entries'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)  # Renamed from 'metadata' as it's a reserved word
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<LogEntry(id={self.id}, event_type='{self.event_type}')>"