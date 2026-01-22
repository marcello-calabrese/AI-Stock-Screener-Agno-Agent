"""
UI Components for the AI Stock Screener Streamlit application.

This module contains reusable UI components,
keeping the presentation logic separate from business logic.
"""

import streamlit as st
from typing import Callable

from config import app_config
from session_manager import SessionManager
from api_client import APIClient


class HeaderComponent:
    """Header section of the application."""
    
    @staticmethod
    def render(session: SessionManager) -> None:
        """
        Render the header component.
        
        Args:
            session: The session manager for state access.
        """
        st.title("AI Stock Screener Agno Agent")
        st.header(
            "Welcome to the AI Stock Screener Agno Agent! "
            "This application leverages advanced AI capabilities "
            "to help you analyze and screen stocks effectively."
        )
        
        # API Status indicator
        if session.api_healthy:
            st.success("✅ Connected to API")
        else:
            st.error(
                "❌ API Server not available. "
                "Please start it with: `uv run uvicorn api:app --reload --port 8000`"
            )
            if st.button("🔄 Retry Connection"):
                if session.check_and_update_health():
                    session.ensure_session()
                st.rerun()


class HeroComponent:
    """Hero section with image and tagline."""
    
    @staticmethod
    def render() -> None:
        """Render the hero component."""
        st.write("")
        st.write("")
        
        with st.container():
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(app_config.image_path, width=app_config.image_width)
                st.markdown(
                    "<h3 style='text-align: center;'>Ready to find best stocks?</h3>",
                    unsafe_allow_html=True
                )
        
        st.write("")
        st.write("")
        
        with st.container():
            st.markdown(
                "<h2 style='text-align: center;'>Chat with the AI Stock Screener Agent</h2>",
                unsafe_allow_html=True
            )
        
        st.write("")


class ChatComponent:
    """Chat interface component."""
    
    def __init__(self, session: SessionManager, client: APIClient):
        """
        Initialize the chat component.
        
        Args:
            session: The session manager for state access.
            client: The API client for chat operations.
        """
        self._session = session
        self._client = client
    
    def render(self) -> None:
        """Render the chat component."""
        self._render_message_history()
        self._handle_user_input()
    
    def _render_message_history(self) -> None:
        """Render the chat message history."""
        for message in self._session.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def _handle_user_input(self) -> None:
        """Handle user input and generate response."""
        prompt = st.chat_input(
            placeholder="Example: Ask the AI stock screener to suggest 5 stocks to invest in the US market.",
            disabled=not self._session.api_healthy
        )
        
        if prompt:
            self._process_message(prompt)
    
    def _process_message(self, prompt: str) -> None:
        """
        Process a user message and get agent response.
        
        Args:
            prompt: The user's message.
        """
        # Add and display user message
        self._session.add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display agent response
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                if self._session.use_streaming:
                    response = self._get_streaming_response(prompt)
                else:
                    response = self._get_regular_response(prompt)
                
                if response:
                    self._session.add_message("assistant", response)
    
    def _get_streaming_response(self, prompt: str) -> str:
        """
        Get a streaming response from the agent.
        
        Args:
            prompt: The user's message.
            
        Returns:
            The complete response text.
        """
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            for content, session_id, is_error in self._client.chat_stream(
                prompt,
                self._session.session_id,
                self._session.user_id
            ):
                if is_error:
                    st.error(content)
                    return ""
                
                full_response += content
                self._session.session_id = session_id
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            return full_response
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return ""
    
    def _get_regular_response(self, prompt: str) -> str:
        """
        Get a non-streaming response from the agent.
        
        Args:
            prompt: The user's message.
            
        Returns:
            The complete response text.
        """
        message_placeholder = st.empty()
        
        try:
            response = self._client.chat(
                prompt,
                self._session.session_id,
                self._session.user_id
            )
            
            if response.success:
                self._session.session_id = response.session_id
                message_placeholder.markdown(response.content)
                return response.content
            else:
                st.error(response.error)
                return ""
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return ""


class SidebarComponent:
    """Sidebar component with settings and actions."""
    
    def __init__(self, session: SessionManager, client: APIClient):
        """
        Initialize the sidebar component.
        
        Args:
            session: The session manager for state access.
            client: The API client for API info.
        """
        self._session = session
        self._client = client
    
    def render(self) -> None:
        """Render the sidebar component."""
        with st.sidebar:
            self._render_settings()
            st.divider()
            self._render_session_info()
            st.divider()
            self._render_actions()
            st.divider()
            self._render_api_info()
    
    def _render_settings(self) -> None:
        """Render the settings section."""
        st.markdown("# 🔧 Settings")
        self._session.use_streaming = st.toggle(
            "Use Streaming",
            value=self._session.use_streaming
        )
    
    def _render_session_info(self) -> None:
        """Render the session information section."""
        st.markdown("# 📊 Session Information")
        
        status_icon = "🟢" if self._session.api_healthy else "🔴"
        status_text = "Connected" if self._session.api_healthy else "Disconnected"
        st.write(f"**API Status:** {status_icon} {status_text}")
        
        st.write(f"**Session ID:** {self._session.session_id_display}")
        st.write(f"**User ID:** {self._session.user_id}")
        
        st.caption(
            "This information helps maintain context and memory "
            "for your interactions with the AI Stock Screener Agent."
        )
    
    def _render_actions(self) -> None:
        """Render the actions section."""
        st.markdown("# 🎯 Actions")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            self._session.clear_messages()
            st.rerun()
        
        if st.button("🔄 New Session", use_container_width=True):
            if self._session.create_new_session():
                st.rerun()
            else:
                st.error("Failed to create new session. Is the API running?")
        
        if st.button("🔌 Reconnect to API", use_container_width=True):
            self._session.reconnect()
            st.rerun()
    
    def _render_api_info(self) -> None:
        """Render the API information section."""
        st.markdown("# ℹ️ API Info")
        st.code(f"API URL: {self._client.base_url}", language=None)
        st.caption("Make sure the API server is running before using this app.")
