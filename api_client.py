"""
API Client for communicating with the AI Stock Screener FastAPI backend.

This module handles all HTTP communication with the API server,
including health checks, session management, and chat functionality.
"""

import json
from typing import Generator, Tuple, Optional
from dataclasses import dataclass
import requests

from config import APIConfig, api_config


@dataclass
class ChatResponse:
    """Response from a chat request."""
    content: str
    session_id: str
    success: bool
    error: Optional[str] = None


class APIClient:
    """
    Client for interacting with the AI Stock Screener API.
    
    Handles all HTTP communication including health checks,
    session management, and both streaming and non-streaming chat.
    """
    
    def __init__(self, config: APIConfig = api_config):
        """
        Initialize the API client.
        
        Args:
            config: API configuration settings.
        """
        self._config = config
    
    @property
    def base_url(self) -> str:
        """Get the API base URL."""
        return self._config.base_url
    
    def check_health(self) -> bool:
        """
        Check if the API server is running and healthy.
        
        Returns:
            True if the API is healthy, False otherwise.
        """
        try:
            response = requests.get(
                f"{self._config.base_url}{self._config.health_endpoint}",
                timeout=self._config.timeout_short
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def create_session(self) -> Optional[str]:
        """
        Create a new session via the API.
        
        Returns:
            The new session ID, or None if creation failed.
        """
        try:
            response = requests.post(
                f"{self._config.base_url}{self._config.session_endpoint}",
                timeout=self._config.timeout_short
            )
            if response.status_code == 200:
                return response.json()["session_id"]
        except requests.exceptions.RequestException:
            pass
        return None
    
    def chat(self, message: str, session_id: str, user_id: str) -> ChatResponse:
        """
        Send a message to the agent and get a complete response.
        
        Args:
            message: The user's message.
            session_id: The session ID for conversation context.
            user_id: The user identifier.
            
        Returns:
            ChatResponse containing the agent's response.
        """
        try:
            response = requests.post(
                f"{self._config.base_url}{self._config.chat_endpoint}",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id
                },
                timeout=self._config.timeout_long
            )
            
            if response.status_code == 200:
                data = response.json()
                return ChatResponse(
                    content=data["response"],
                    session_id=data["session_id"],
                    success=True
                )
            else:
                return ChatResponse(
                    content="",
                    session_id=session_id,
                    success=False,
                    error=f"Error: {response.status_code} - {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            return ChatResponse(
                content="",
                session_id=session_id,
                success=False,
                error=f"Connection error: {e}"
            )
    
    def chat_stream(
        self, 
        message: str, 
        session_id: str, 
        user_id: str
    ) -> Generator[Tuple[str, str, bool], None, None]:
        """
        Send a message to the agent and stream the response.
        
        Args:
            message: The user's message.
            session_id: The session ID for conversation context.
            user_id: The user identifier.
            
        Yields:
            Tuples of (content_chunk, session_id, is_error).
        """
        try:
            response = requests.post(
                f"{self._config.base_url}{self._config.stream_endpoint}",
                json={
                    "message": message,
                    "session_id": session_id,
                    "user_id": user_id
                },
                stream=True,
                timeout=self._config.timeout_long
            )
            
            current_session_id = session_id
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        yield from self._parse_sse_line(line_str, current_session_id)
                        
        except requests.exceptions.RequestException as e:
            yield f"Connection error: {e}", session_id, True
    
    def _parse_sse_line(
        self, 
        line: str, 
        current_session_id: str
    ) -> Generator[Tuple[str, str, bool], None, None]:
        """
        Parse a Server-Sent Events line.
        
        Args:
            line: The SSE line to parse.
            current_session_id: The current session ID.
            
        Yields:
            Tuples of (content, session_id, is_error).
        """
        try:
            data = json.loads(line[6:])  # Skip 'data: ' prefix
            
            session_id = data.get("session_id", current_session_id)
            
            if "content" in data:
                # Unescape the content
                content = data["content"].replace("\\n", "\n").replace('\\"', '"')
                yield content, session_id, False
                
            if "error" in data:
                yield data["error"], session_id, True
                
        except json.JSONDecodeError:
            pass


# Default client instance
api_client = APIClient()
