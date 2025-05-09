#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI Assistant module for Telegram Group Manager Bot.
This module provides AI-powered chat capabilities using OpenAI's API.
"""

import logging
import datetime
import json
import os
from typing import Dict, List, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Check if OpenAI API key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
has_openai = False

try:
    from openai import OpenAI
    has_openai = OPENAI_API_KEY is not None
except ImportError:
    logger.warning("OpenAI package not installed. AI chat features will be disabled.")

# Initialize OpenAI client if API key is available
openai_client = None
if has_openai:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        has_openai = False

# Conversation contexts for different use cases
CONVERSATION_CONTEXTS = {
    "orthodox_church": {
        "system_prompt": (
            "You are a helpful assistant for an Ethiopian Orthodox Church community. "
            "Provide respectful, informative responses about Orthodox traditions, "
            "theology, history, and practices. Focus particularly on Ethiopian Orthodox "
            "traditions like Timkat, Meskel, and other unique aspects of this ancient "
            "Christian tradition. Avoid political topics and focus on spiritual guidance."
        ),
        "example_questions": [
            "What is the significance of Timkat?",
            "When is the next fasting period?",
            "What does the Bible say about forgiveness?",
            "How do I prepare for Holy Communion?",
            "What are the main feast days in Ethiopian Orthodox tradition?"
        ]
    },
    "education": {
        "system_prompt": (
            "You are a helpful assistant for an educational institution. "
            "Provide informative, accurate responses to academic questions, "
            "help with homework understanding (without directly solving problems), "
            "explain concepts, and offer study advice. You should be encouraging "
            "and supportive, helping students learn rather than just giving answers."
        ),
        "example_questions": [
            "Can you explain photosynthesis?",
            "What are some study techniques for memorizing vocabulary?",
            "How do I structure an essay?",
            "What's the difference between kinetic and potential energy?",
            "Can you recommend resources for learning calculus?"
        ]
    },
    "photography": {
        "system_prompt": (
            "You are a helpful assistant for a photography and film business. "
            "Provide knowledgeable responses about photography techniques, equipment, "
            "composition, lighting, post-processing, and filming. Offer creative ideas "
            "and professional advice about capturing different subjects and events."
        ),
        "example_questions": [
            "What's the best aperture for portrait photography?",
            "How can I improve indoor lighting for filming?",
            "What equipment do I need for a basic photography setup?",
            "How should I pose subjects for a family portrait?",
            "What's the difference between RAW and JPEG formats?"
        ]
    },
    "general": {
        "system_prompt": (
            "You are a helpful assistant in a group chat. Provide friendly, informative, "
            "and concise responses to general questions. Be respectful of all users and "
            "avoid contentious topics. If asked about specific expertise outside your "
            "knowledge, acknowledge limitations and suggest seeking appropriate experts."
        ),
        "example_questions": [
            "What's the weather like today?",
            "Can you explain the rules of soccer?",
            "What are some good books to read?",
            "How do I cook pasta properly?",
            "What's the capital of Ethiopia?"
        ]
    }
}

# Maximum conversation history to maintain per user
MAX_CONVERSATION_HISTORY = 10

# User conversation storage
# Structure: {user_id: {context: "context_name", history: [{role: "", content: ""}, ...]}}
user_conversations = {}

def generate_ai_response(user_id: int, message: str, context_type: str = "general") -> str:
    """
    Generate an AI response using OpenAI API.
    
    Args:
        user_id: The user's ID
        message: The user's message
        context_type: The conversation context type
        
    Returns:
        str: AI-generated response
    """
    if not has_openai or not openai_client:
        return "I'm sorry, but the AI assistant is currently unavailable."
    
    try:
        # Get or initialize user conversation
        if user_id not in user_conversations:
            user_conversations[user_id] = {
                "context": context_type,
                "history": []
            }
        
        # If context has changed, reset history
        if user_conversations[user_id]["context"] != context_type:
            user_conversations[user_id] = {
                "context": context_type,
                "history": []
            }
        
        # Get system prompt based on context
        system_prompt = CONVERSATION_CONTEXTS.get(
            context_type, CONVERSATION_CONTEXTS["general"]
        )["system_prompt"]
        
        # Construct messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(user_conversations[user_id]["history"])
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Generate response
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # Use the newest model, gpt-4o
            messages=messages,
            max_tokens=500
        )
        
        # Extract and return the response content
        assistant_message = response.choices[0].message.content
        
        # Update conversation history
        user_conversations[user_id]["history"].append({"role": "user", "content": message})
        user_conversations[user_id]["history"].append({"role": "assistant", "content": assistant_message})
        
        # Limit history size
        if len(user_conversations[user_id]["history"]) > MAX_CONVERSATION_HISTORY * 2:
            user_conversations[user_id]["history"] = user_conversations[user_id]["history"][-MAX_CONVERSATION_HISTORY*2:]
        
        return assistant_message
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return f"I'm sorry, but I encountered an error: {str(e)}"

def reset_conversation(user_id: int) -> bool:
    """
    Reset the conversation history for a user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if user_id in user_conversations:
            context = user_conversations[user_id]["context"]
            user_conversations[user_id] = {
                "context": context,
                "history": []
            }
        return True
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        return False

def set_conversation_context(user_id: int, context_type: str) -> bool:
    """
    Set the conversation context for a user.
    
    Args:
        user_id: The user's ID
        context_type: The conversation context type
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if context_type not in CONVERSATION_CONTEXTS:
            return False
            
        if user_id in user_conversations:
            user_conversations[user_id]["context"] = context_type
            user_conversations[user_id]["history"] = []
        else:
            user_conversations[user_id] = {
                "context": context_type,
                "history": []
            }
        return True
    except Exception as e:
        logger.error(f"Error setting conversation context: {e}")
        return False

def get_available_contexts() -> List[str]:
    """
    Get list of available conversation contexts.
    
    Returns:
        List[str]: List of context names
    """
    return list(CONVERSATION_CONTEXTS.keys())

def get_context_description(context_type: str) -> str:
    """
    Get the description of a conversation context.
    
    Args:
        context_type: The context type
        
    Returns:
        str: Description of the context
    """
    if context_type not in CONVERSATION_CONTEXTS:
        return "Unknown context type"
        
    return CONVERSATION_CONTEXTS[context_type]["system_prompt"]

def get_example_questions(context_type: str) -> List[str]:
    """
    Get example questions for a conversation context.
    
    Args:
        context_type: The context type
        
    Returns:
        List[str]: List of example questions
    """
    if context_type not in CONVERSATION_CONTEXTS:
        return []
        
    return CONVERSATION_CONTEXTS[context_type]["example_questions"]

def format_ai_context_message() -> str:
    """
    Format a message explaining the available AI conversation contexts.
    
    Returns:
        str: Formatted message
    """
    if not has_openai:
        return (
            "🤖 *AI Assistant (Currently Unavailable)*\n\n"
            "The AI assistant requires an OpenAI API key to function. "
            "Please ask the administrator to set up the OpenAI integration."
        )
    
    message = "🤖 *AI Assistant Contexts*\n\n"
    
    for context_name in CONVERSATION_CONTEXTS:
        examples = CONVERSATION_CONTEXTS[context_name]["example_questions"]
        example_str = examples[0] if examples else "No examples available"
        
        message += (
            f"*{context_name.replace('_', ' ').title()}*\n"
            f"Example: \"{example_str}\"\n"
            f"_Use /ai_{context_name} to set this context_\n\n"
        )
    
    message += (
        "You can chat with the AI by using /ai followed by your question.\n"
        "Use /ai_reset to reset your conversation history."
    )
    
    return message