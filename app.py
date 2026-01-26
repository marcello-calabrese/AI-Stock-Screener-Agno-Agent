import streamlit as st
import uuid
from agno.agent import RunEvent
from dotenv import load_dotenv

# Load environment variables from .env file
#load_dotenv()

# Cache the agent (created only once, not on every rerun)
@st.cache_resource
def get_agent():
    from agents import ai_stock_analysis_agent
    return ai_stock_analysis_agent

# Initialize session state efficiently
def init_session_state():
    defaults = {
        "messages": [],
        "session_id": str(uuid.uuid4()),
        "user_id": "default_user"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize
init_session_state()
agent = get_agent()

### Streamlit APP Header ###

st.set_page_config(
    page_title="AI Stock Screener Agno Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AI Stock Screener Agno Agent")
st.header("Welcome to the AI Stock Screener Agno Agent! This application leverages advanced AI capabilities to help you analyze and screen stocks effectively.")
# Add some spacing
st.write("")
st.write("")
st.write("") 
st.write("")
 

with st.container(vertical_alignment="top",horizontal_alignment="center"):
    st.image("assets/sphere2.jpg", width=300)
    st.header(text_alignment="center", body="Ready to find best stocks?")
    
st.write("")
st.write("")
   
with st.container(horizontal_alignment="center", vertical_alignment="center"):# Example usage of the Team Agent Coordinator
    
    st.title(text_alignment="center", body="Chat with the AI Stock Screener Agent")
    
st.write("")
    
with st.container(horizontal_alignment="center", vertical_alignment="center"):

        
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input(placeholder="Example: Ask the AI stock screener to suggest 5 stocks to invest in the US market."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                # Create a placeholder for the streaming response
                message_placeholder = st.empty()
                full_response = ""
                try:
                    # Stream the agent response
                    stream = agent.run(
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
                    st.error(f"An error occurred: {e}")
                    
    # Sidebar with session info
    with st.sidebar:
        st.markdown("# Session Information")
        st.write(f"**Session ID:** {st.session_state.session_id}")
        st.write(f"**User ID:** {st.session_state.user_id}")
        st.write("This information helps maintain context and memory for your interactions with the AI Stock Screener Agent.")
        
        if st.button("Clear chat history"):
            st.session_state.messages = []
            st.rerun()
            
        # Generate new session id from fresh start
        if st.button("New Session"):
            
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()


