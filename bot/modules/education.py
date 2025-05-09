#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Education module for Telegram Group Manager Bot.
This module provides specialized functions for educational institutions
to manage student, teacher, and parent communications.
"""

import logging
import datetime
from typing import Dict, List, Optional, Tuple
import re

# Set up logging
logger = logging.getLogger(__name__)

# User roles in educational context
EDUCATION_ROLES = {
    "student": 10,
    "parent": 20,
    "teacher": 50,
    "department_head": 75,
    "administrator": 100
}

# Assignment status options
ASSIGNMENT_STATUS = [
    "assigned",
    "in_progress",
    "submitted",
    "graded",
    "returned"
]

# Question types
QUESTION_TYPES = [
    "multiple_choice",
    "essay",
    "short_answer",
    "file_upload"
]

class Assignment:
    """Class representing a school assignment"""
    
    def __init__(self, title, description, due_date, assigned_by, class_id=None, grade_level=None):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.assigned_by = assigned_by
        self.class_id = class_id
        self.grade_level = grade_level
        self.status = "assigned"
        self.submissions = {}
        self.created_at = datetime.datetime.now()
    
    def to_dict(self):
        """Convert assignment to dictionary for storage"""
        return {
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if isinstance(self.due_date, datetime.datetime) else self.due_date,
            "assigned_by": self.assigned_by,
            "class_id": self.class_id,
            "grade_level": self.grade_level,
            "status": self.status,
            "submissions": self.submissions,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create assignment from dictionary"""
        obj = cls(
            title=data.get("title"),
            description=data.get("description"),
            due_date=data.get("due_date"),
            assigned_by=data.get("assigned_by"),
            class_id=data.get("class_id"),
            grade_level=data.get("grade_level")
        )
        obj.status = data.get("status", "assigned")
        obj.submissions = data.get("submissions", {})
        if isinstance(data.get("created_at"), str):
            obj.created_at = datetime.datetime.fromisoformat(data.get("created_at"))
        return obj

class Question:
    """Class representing an educational question"""
    
    def __init__(self, text, question_type, options=None, correct_answer=None, asked_by=None):
        self.text = text
        self.question_type = question_type
        self.options = options or []
        self.correct_answer = correct_answer
        self.asked_by = asked_by
        self.replies = []
        self.created_at = datetime.datetime.now()
    
    def to_dict(self):
        """Convert question to dictionary for storage"""
        return {
            "text": self.text,
            "question_type": self.question_type,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "asked_by": self.asked_by,
            "replies": self.replies,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create question from dictionary"""
        obj = cls(
            text=data.get("text"),
            question_type=data.get("question_type"),
            options=data.get("options"),
            correct_answer=data.get("correct_answer"),
            asked_by=data.get("asked_by")
        )
        obj.replies = data.get("replies", [])
        if isinstance(data.get("created_at"), str):
            obj.created_at = datetime.datetime.fromisoformat(data.get("created_at"))
        return obj
    
    def add_reply(self, text, user_id, is_correct=None):
        """Add a reply to the question"""
        reply = {
            "text": text,
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "is_correct": is_correct
        }
        self.replies.append(reply)
        return reply

def parse_assignment_command(text: str) -> Optional[Dict]:
    """
    Parse assignment command from text.
    Format: /assignment "Title" "Description" "YYYY-MM-DD" [#class_id] [grade:level]
    
    Args:
        text: The command text to parse
        
    Returns:
        Optional[Dict]: Assignment data if valid command, None otherwise
    """
    # Extract quoted strings
    pattern = r'"([^"]*)"'
    quotes = re.findall(pattern, text)
    
    if len(quotes) < 3:
        return None
    
    title = quotes[0]
    description = quotes[1]
    date_str = quotes[2]
    
    try:
        due_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None
    
    # Extract optional class ID
    class_id = None
    class_match = re.search(r'#(\w+)', text)
    if class_match:
        class_id = class_match.group(1)
    
    # Extract optional grade level
    grade_level = None
    grade_match = re.search(r'grade:(\w+)', text)
    if grade_match:
        grade_level = grade_match.group(1)
    
    return {
        "title": title,
        "description": description,
        "due_date": due_date,
        "class_id": class_id,
        "grade_level": grade_level
    }

def format_assignment_message(assignment: Dict) -> str:
    """
    Format assignment data into human-readable message.
    
    Args:
        assignment: Assignment data dictionary
        
    Returns:
        str: Formatted message
    """
    due_date = assignment.get("due_date")
    if isinstance(due_date, str):
        try:
            due_date = datetime.datetime.fromisoformat(due_date)
        except ValueError:
            pass
    
    if isinstance(due_date, datetime.datetime):
        due_date_str = due_date.strftime("%A, %B %d, %Y")
    else:
        due_date_str = str(due_date)
    
    message = (
        f"📚 *ASSIGNMENT: {assignment.get('title')}*\n\n"
        f"📝 *Description:*\n{assignment.get('description')}\n\n"
        f"📅 *Due Date:* {due_date_str}\n"
    )
    
    if assignment.get("class_id"):
        message += f"🏫 *Class:* {assignment.get('class_id')}\n"
    
    if assignment.get("grade_level"):
        message += f"📊 *Grade Level:* {assignment.get('grade_level')}\n"
    
    message += f"\n*Status:* {assignment.get('status', 'assigned')}"
    
    return message

def parse_question_command(text: str) -> Optional[Dict]:
    """
    Parse question command from text.
    Format: /question "Question text" [type:question_type] [options:"A|B|C"] [answer:correct_answer]
    
    Args:
        text: The command text to parse
        
    Returns:
        Optional[Dict]: Question data if valid command, None otherwise
    """
    # Extract the main question text
    question_match = re.search(r'"([^"]*)"', text)
    if not question_match:
        return None
    
    question_text = question_match.group(1)
    
    # Default to short_answer if type not specified
    question_type = "short_answer"
    type_match = re.search(r'type:(\w+)', text)
    if type_match:
        q_type = type_match.group(1)
        if q_type in QUESTION_TYPES:
            question_type = q_type
    
    # Extract options for multiple choice
    options = []
    options_match = re.search(r'options:"([^"]*)"', text)
    if options_match:
        options_str = options_match.group(1)
        options = [opt.strip() for opt in options_str.split("|")]
    
    # Extract correct answer if provided
    correct_answer = None
    answer_match = re.search(r'answer:(\w+)', text)
    if answer_match:
        correct_answer = answer_match.group(1)
    
    return {
        "text": question_text,
        "question_type": question_type,
        "options": options,
        "correct_answer": correct_answer
    }

def format_question_message(question: Dict) -> str:
    """
    Format question data into human-readable message.
    
    Args:
        question: Question data dictionary
        
    Returns:
        str: Formatted message
    """
    message = f"❓ *QUESTION:*\n{question.get('text')}\n\n"
    
    question_type = question.get('question_type')
    if question_type == 'multiple_choice':
        message += "*Options:*\n"
        for i, option in enumerate(question.get('options', [])):
            letter = chr(65 + i)  # A, B, C, etc.
            message += f"{letter}. {option}\n"
        
        message += "\nReply with the letter of your choice."
    elif question_type == 'essay':
        message += "*This is an essay question.*\nPlease provide a detailed response."
    elif question_type == 'short_answer':
        message += "*This is a short answer question.*\nPlease answer briefly."
    elif question_type == 'file_upload':
        message += "*Please upload your answer as a file.*"
    
    return message

def get_upcoming_assignments(assignments: List[Dict], days_ahead: int = 7) -> List[Dict]:
    """
    Get list of upcoming assignments due within specified days.
    
    Args:
        assignments: List of assignment dictionaries
        days_ahead: Number of days to look ahead
        
    Returns:
        List[Dict]: Filtered list of upcoming assignments
    """
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today + datetime.timedelta(days=days_ahead)
    
    upcoming = []
    
    for assignment in assignments:
        due_date = assignment.get("due_date")
        
        # Convert string date to datetime if needed
        if isinstance(due_date, str):
            try:
                due_date = datetime.datetime.fromisoformat(due_date)
            except ValueError:
                continue
        
        # Skip if due date is not valid
        if not isinstance(due_date, datetime.datetime):
            continue
            
        # Check if due within the specified range
        if today <= due_date <= end_date:
            upcoming.append(assignment)
    
    # Sort by due date
    upcoming.sort(key=lambda x: x.get("due_date"))
    
    return upcoming

def format_upcoming_assignments_message(assignments: List[Dict]) -> str:
    """
    Format a list of upcoming assignments into a human-readable message.
    
    Args:
        assignments: List of assignment dictionaries
        
    Returns:
        str: Formatted message
    """
    if not assignments:
        return "📝 *Upcoming Assignments*\n\nNo assignments due soon."
    
    message = "📝 *Upcoming Assignments*\n\n"
    
    for i, assignment in enumerate(assignments, 1):
        due_date = assignment.get("due_date")
        
        # Convert string date to datetime if needed
        if isinstance(due_date, str):
            try:
                due_date = datetime.datetime.fromisoformat(due_date)
                due_date_str = due_date.strftime("%A, %B %d")
            except ValueError:
                due_date_str = due_date
        else:
            due_date_str = due_date.strftime("%A, %B %d") if isinstance(due_date, datetime.datetime) else str(due_date)
            
        message += (
            f"{i}. *{assignment.get('title')}*\n"
            f"   Due: {due_date_str}\n"
        )
        
        if assignment.get("class_id"):
            message += f"   Class: {assignment.get('class_id')}\n"
            
        message += "\n"
    
    return message

def check_education_role_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user has sufficient permissions based on educational role.
    
    Args:
        user_role: The user's role
        required_role: The minimum role required
        
    Returns:
        bool: True if user has sufficient permissions, False otherwise
    """
    user_level = EDUCATION_ROLES.get(user_role, 0)
    required_level = EDUCATION_ROLES.get(required_role, 0)
    
    return user_level >= required_level