"""Shared dependency helpers for the FastAPI application."""
from __future__ import annotations

from typing import Dict
from uuid import uuid4

from src.memory.conversation_manager import ConversationManager, UserProfileManager

_conversations: Dict[str, ConversationManager] = {}
_profile_manager = UserProfileManager()


def get_profile_manager() -> UserProfileManager:
    """Return the singleton profile manager."""
    return _profile_manager


def get_conversation_manager(session_id: str | None = None) -> tuple[str, ConversationManager]:
    """Return (session_id, manager), creating storage as needed."""
    if not session_id:
        session_id = uuid4().hex
    manager = _conversations.get(session_id)
    if manager is None:
        manager = ConversationManager()
        stored_messages = manager.load_session(session_id)
        if stored_messages:
            manager.current_session = stored_messages
        _conversations[session_id] = manager
    return session_id, manager
