"""
Session state management for the Streamlit application.

This module handles all session state operations,
keeping the state management logic separate from the UI.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import streamlit as st

from config import app_config
from api_client import APIClient, api_client


@dataclass
class Message:
    """A chat message."""
    role: str
    content: str


@dataclass
class SessionState:
    """Application session state."""
    messages: List[Message] = field(default_factory=list)
    session_id: Optional[str] = None
    user_id: str = app_config.default_user_id
    use_streaming: bool = True
    api_healthy: bool = False


class SessionManager:
    """
    Manages the Streamlit session state.
    
    Provides a clean interface for accessing and modifying
    session state without directly coupling to st.session_state.
    """
    
    def __init__(self, client: APIClient = api_client):
        """
        Initialize the session manager.
        
        Args:
            client: The API client for session operations.
        """
        self._client = client
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize session state with default values if not present."""
        defaults = {
            "messages": [],
            "session_id": None,
            "user_id": app_config.default_user_id,
            "use_streaming": True,
            "api_healthy": False
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    # --------------------- Properties --------------------- #
    
    @property
    def messages(self) -> List[Dict[str, str]]:
        """Get the list of chat messages."""
        return st.session_state.messages
    
    @property
    def session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return st.session_state.session_id
    
    @session_id.setter
    def session_id(self, value: str) -> None:
        """Set the session ID."""
        st.session_state.session_id = value
    
    @property
    def user_id(self) -> str:
        """Get the current user ID."""
        return st.session_state.user_id
    
    @property
    def use_streaming(self) -> bool:
        """Get the streaming preference."""
        return st.session_state.use_streaming
    
    @use_streaming.setter
    def use_streaming(self, value: bool) -> None:
        """Set the streaming preference."""
        st.session_state.use_streaming = value
    
    @property
    def api_healthy(self) -> bool:
        """Get the API health status."""
        return st.session_state.api_healthy
    
    @api_healthy.setter
    def api_healthy(self, value: bool) -> None:
        """Set the API health status."""
        st.session_state.api_healthy = value
    
    @property
    def session_id_display(self) -> str:
        """Get a shortened session ID for display."""
        if self.session_id:
            return f"{self.session_id[:8]}..."
        return "None"
    
    # --------------------- Message Operations --------------------- #
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the chat history.
        
        Args:
            role: The message role ('user' or 'assistant').
            content: The message content.
        """
        st.session_state.messages.append({"role": role, "content": content})
    
    def clear_messages(self) -> None:
        """Clear all chat messages."""
        st.session_state.messages = []
    
    # --------------------- Session Operations --------------------- #
    
    def check_and_update_health(self) -> bool:
        """
        Check API health and update the state.
        
        Returns:
            True if the API is healthy.
        """
        self.api_healthy = self._client.check_health()
        return self.api_healthy
    
    def ensure_session(self) -> bool:
        """
        Ensure a valid session exists.
        
        Creates a new session if one doesn't exist and the API is healthy.
        
        Returns:
            True if a valid session exists.
        """
        if not self.api_healthy:
            self.check_and_update_health()
        
        if self.api_healthy and not self.session_id:
            new_session = self._client.create_session()
            if new_session:
                self.session_id = new_session
                return True
            return False
        
        return self.session_id is not None
    
    def create_new_session(self) -> bool:
        """
        Create a new session and clear chat history.
        
        Returns:
            True if the new session was created successfully.
        """
        new_session = self._client.create_session()
        if new_session:
            self.session_id = new_session
            self.clear_messages()
            return True
        return False
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to the API.
        
        Returns:
            True if reconnection was successful.
        """
        if self.check_and_update_health():
            if not self.session_id:
                self._client.create_session()
            return True
        return False
