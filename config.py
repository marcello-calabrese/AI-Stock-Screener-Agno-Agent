"""
Configuration settings for the AI Stock Screener application.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class APIConfig:
    """API configuration settings."""
    base_url: str = "http://localhost:8000"
    health_endpoint: str = "/api/health"
    session_endpoint: str = "/api/session/new"
    chat_endpoint: str = "/api/chat"
    stream_endpoint: str = "/api/chat/stream"
    timeout_short: int = 5
    timeout_long: int = 120


@dataclass(frozen=True)
class AppConfig:
    """Application configuration settings."""
    page_title: str = "AI Stock Screener Agno Agent"
    page_layout: str = "wide"
    default_user_id: str = "default_user"
    image_path: str = "assets/sphere2.jpg"
    image_width: int = 300


# Default configurations
api_config = APIConfig()
app_config = AppConfig()
