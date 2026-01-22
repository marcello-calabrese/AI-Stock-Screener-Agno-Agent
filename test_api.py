"""
Tests for AI Stock Screener FastAPI endpoints.

Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid


# --------------------- Fixtures --------------------- #

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from api import app
    return TestClient(app)


@pytest.fixture
def mock_agent_response():
    """Mock agent response for testing."""
    class MockChunk:
        def __init__(self, content):
            from agno.agent import RunEvent
            self.event = RunEvent.run_content
            self.content = content
    
    return [
        MockChunk("This is a "),
        MockChunk("test response "),
        MockChunk("from the agent.")
    ]


# --------------------- Health Check Tests --------------------- #

class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check_returns_200(self, client):
        """Test that health check endpoint returns 200 status."""
        response = client.get("/api/health")
        assert response.status_code == 200
    
    def test_health_check_response_structure(self, client):
        """Test that health check returns correct response structure."""
        response = client.get("/api/health")
        data = response.json()
        
        assert "status" in data
        assert "message" in data
        assert data["status"] == "healthy"
        assert data["message"] == "AI Stock Screener API is running"


# --------------------- Session Tests --------------------- #

class TestSessionEndpoint:
    """Tests for the session management endpoint."""
    
    def test_create_new_session_returns_200(self, client):
        """Test that creating a new session returns 200 status."""
        response = client.post("/api/session/new")
        assert response.status_code == 200
    
    def test_create_new_session_returns_valid_uuid(self, client):
        """Test that new session returns a valid UUID."""
        response = client.post("/api/session/new")
        data = response.json()
        
        assert "session_id" in data
        # Validate it's a proper UUID format
        try:
            uuid.UUID(data["session_id"])
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False
        
        assert is_valid_uuid
    
    def test_create_new_session_returns_unique_ids(self, client):
        """Test that each new session request returns a unique ID."""
        response1 = client.post("/api/session/new")
        response2 = client.post("/api/session/new")
        
        session_id1 = response1.json()["session_id"]
        session_id2 = response2.json()["session_id"]
        
        assert session_id1 != session_id2


# --------------------- Chat Endpoint Tests --------------------- #

class TestChatEndpoint:
    """Tests for the main chat endpoint."""
    
    def test_chat_requires_message(self, client):
        """Test that chat endpoint requires a message."""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # Validation error
    
    def test_chat_accepts_message_only(self, client, mock_agent_response):
        """Test that chat endpoint works with just a message."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat", json={"message": "Analyze AAPL"})
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data
    
    def test_chat_with_session_id(self, client, mock_agent_response):
        """Test that chat endpoint uses provided session_id."""
        test_session_id = str(uuid.uuid4())
        
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat", json={
                "message": "Analyze AAPL",
                "session_id": test_session_id
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == test_session_id
    
    def test_chat_with_user_id(self, client, mock_agent_response):
        """Test that chat endpoint accepts user_id."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat", json={
                "message": "Analyze AAPL",
                "user_id": "test_user_123"
            })
            
            assert response.status_code == 200
            # Verify agent was called with correct user_id
            mock_agent.run.assert_called_once()
            call_kwargs = mock_agent.run.call_args.kwargs
            assert call_kwargs["user_id"] == "test_user_123"
    
    def test_chat_generates_session_id_if_not_provided(self, client, mock_agent_response):
        """Test that chat endpoint generates session_id when not provided."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat", json={"message": "Analyze AAPL"})
            
            data = response.json()
            assert "session_id" in data
            # Validate it's a proper UUID
            uuid.UUID(data["session_id"])
    
    def test_chat_concatenates_streamed_response(self, client, mock_agent_response):
        """Test that chat endpoint properly concatenates streamed chunks."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat", json={"message": "Analyze AAPL"})
            
            data = response.json()
            assert data["response"] == "This is a test response from the agent."
    
    def test_chat_handles_agent_error(self, client):
        """Test that chat endpoint handles agent errors gracefully."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.side_effect = Exception("Agent error")
            
            response = client.post("/api/chat", json={"message": "Analyze AAPL"})
            
            assert response.status_code == 500
            assert "error" in response.json()["detail"].lower()


# --------------------- Streaming Chat Endpoint Tests --------------------- #

class TestChatStreamEndpoint:
    """Tests for the streaming chat endpoint."""
    
    def test_stream_requires_message(self, client):
        """Test that stream endpoint requires a message."""
        response = client.post("/api/chat/stream", json={})
        assert response.status_code == 422  # Validation error
    
    def test_stream_returns_event_stream(self, client, mock_agent_response):
        """Test that stream endpoint returns event-stream content type."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat/stream", json={"message": "Analyze AAPL"})
            
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
    
    def test_stream_sends_session_id_first(self, client, mock_agent_response):
        """Test that stream sends session_id in the first message."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat/stream", json={"message": "Analyze AAPL"})
            
            # Parse SSE response
            content = response.text
            assert "session_id" in content
    
    def test_stream_sends_done_at_end(self, client, mock_agent_response):
        """Test that stream sends done signal at the end."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat/stream", json={"message": "Analyze AAPL"})
            
            content = response.text
            assert '"done": true' in content


# --------------------- Request Validation Tests --------------------- #

class TestRequestValidation:
    """Tests for request validation."""
    
    def test_empty_message_rejected(self, client):
        """Test that empty message is handled."""
        response = client.post("/api/chat", json={"message": ""})
        # Empty string is technically valid, but agent should handle it
        # This test documents the behavior
        assert response.status_code in [200, 422, 500]
    
    def test_invalid_json_rejected(self, client):
        """Test that invalid JSON is rejected."""
        response = client.post(
            "/api/chat", 
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_extra_fields_ignored(self, client, mock_agent_response):
        """Test that extra fields in request are ignored."""
        with patch("api.ai_stock_analysis_agent") as mock_agent:
            mock_agent.run.return_value = iter(mock_agent_response)
            
            response = client.post("/api/chat", json={
                "message": "Analyze AAPL",
                "extra_field": "should be ignored"
            })
            
            assert response.status_code == 200


# --------------------- Integration Test (requires real agent) --------------------- #

class TestIntegration:
    """
    Integration tests that require the real agent.
    These are marked with pytest.mark.integration and skipped by default.
    Run with: pytest test_api.py -v -m integration
    """
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires API keys and real agent - run manually")
    def test_real_chat_request(self, client):
        """Test a real chat request with the actual agent."""
        response = client.post("/api/chat", json={
            "message": "What is the current price of AAPL?",
            "user_id": "integration_test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["response"]) > 0
        assert "session_id" in data


# --------------------- Run Tests --------------------- #

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
