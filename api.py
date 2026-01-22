from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from dotenv import load_dotenv
from agno.agent import RunEvent

# Load environment variables
load_dotenv()

# Import the agent
from agents import ai_stock_analysis_agent

# Initialize FastAPI app
app = FastAPI(
    title="AI Stock Screener API",
    description="API endpoint for the AI Stock Screener Agno Agent",
    version="1.0.0"
)

# CORS middleware - allow requests from web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------- Pydantic Models --------------------- #

class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message/query")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation history")
    user_id: Optional[str] = Field(default="default_user", description="User identifier")


class ChatResponse(BaseModel):
    response: str = Field(..., description="The agent's response")
    session_id: str = Field(..., description="Session ID used for this conversation")


class SessionResponse(BaseModel):
    session_id: str = Field(..., description="New session ID")


class HealthResponse(BaseModel):
    status: str
    message: str


# --------------------- API Endpoints --------------------- #

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API is running."""
    return HealthResponse(status="healthy", message="AI Stock Screener API is running")


@app.post("/api/session/new", response_model=SessionResponse)
async def create_new_session():
    """Create a new session ID for conversation tracking."""
    new_session_id = str(uuid.uuid4())
    return SessionResponse(session_id=new_session_id)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the AI Stock Screener agent and get a complete response.
    
    - **message**: Your investment analysis query
    - **session_id**: Optional session ID for conversation history (auto-generated if not provided)
    - **user_id**: Optional user identifier for personalization
    """
    try:
        # Generate session_id if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Run the agent and collect full response
        full_response = ""
        stream = ai_stock_analysis_agent.run(
            request.message,
            stream=True,
            session_id=session_id,
            user_id=request.user_id
        )
        
        for chunk in stream:
            if chunk.event == RunEvent.run_content:
                full_response += chunk.content
        
        return ChatResponse(response=full_response, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Send a message to the AI Stock Screener agent and get a streaming response (SSE).
    
    - **message**: Your investment analysis query
    - **session_id**: Optional session ID for conversation history
    - **user_id**: Optional user identifier for personalization
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    async def generate():
        try:
            stream = ai_stock_analysis_agent.run(
                request.message,
                stream=True,
                session_id=session_id,
                user_id=request.user_id
            )
            
            # Send session_id first
            yield f"data: {{\"session_id\": \"{session_id}\"}}\n\n"
            
            for chunk in stream:
                if chunk.event == RunEvent.run_content:
                    # Escape special characters for SSE
                    content = chunk.content.replace("\n", "\\n").replace("\"", "\\\"")
                    yield f"data: {{\"content\": \"{content}\"}}\n\n"
            
            yield "data: {\"done\": true}\n\n"
            
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# --------------------- Run with Uvicorn --------------------- #

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
