import streamlit as st
from agents import ai_stock_analysis_agent
from agno.agent import RunEvent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Test AI Stock Agent",
    layout="centered",
)

st.title("🧪 Test AI Stock Analysis Agent - Streaming")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

if "user_id" not in st.session_state:
    st.session_state.user_id = "test_user"

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input(placeholder="Ask about stocks (e.g., 'Analyze AAPL stock')"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream the agent response
            stream = ai_stock_analysis_agent.run(
                prompt, 
                stream=True,
                session_id=st.session_state.session_id,
                user_id=st.session_state.user_id
            )
            
            # Process streaming chunks
            for chunk in stream:
                if chunk.event == RunEvent.run_content:
                    full_response += chunk.content
                    # Update placeholder with accumulated response
                    message_placeholder.markdown(full_response + "▌")
            
            # Remove cursor and show final response
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar with session info
with st.sidebar:
    st.header("Session Info")
    st.text(f"Session ID: {st.session_state.session_id[:8]}...")
    st.text(f"User ID: {st.session_state.user_id}")
    st.text(f"Messages: {len(st.session_state.messages)}")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
