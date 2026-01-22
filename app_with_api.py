"""
AI Stock Screener Streamlit Application (API Version).

This is the main entry point for the Streamlit application.
It orchestrates the UI components and manages the application flow.

Usage:
    1. Start the API server:
       uv run uvicorn api:app --reload --port 8000
    
    2. Run this app:
       uv run streamlit run app_with_api.py
"""

import streamlit as st

from config import app_config
from api_client import api_client
from session_manager import SessionManager
from ui_components import (
    HeaderComponent,
    HeroComponent,
    ChatComponent,
    SidebarComponent
)


def configure_page() -> None:
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=app_config.page_title,
        layout=app_config.page_layout,
        initial_sidebar_state="expanded",
    )


def initialize_app() -> SessionManager:
    """
    Initialize the application and return the session manager.
    
    Returns:
        Initialized SessionManager instance.
    """
    session = SessionManager(api_client)
    
    # Check API health on first load
    if not session.api_healthy:
        session.check_and_update_health()
    
    # Ensure we have a valid session
    session.ensure_session()
    
    return session


def main() -> None:
    """Main application entry point."""
    # Configure page (must be first Streamlit command)
    configure_page()
    
    # Initialize application
    session = initialize_app()
    
    # Render UI components
    HeaderComponent.render(session)
    HeroComponent.render()
    
    # Chat interface
    chat = ChatComponent(session, api_client)
    chat.render()
    
    # Sidebar
    sidebar = SidebarComponent(session, api_client)
    sidebar.render()


if __name__ == "__main__":
    main()
