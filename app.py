import streamlit as st
from team import team_agent_coordinator

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    st.image("assets/sphere.jpg", width=300)
    st.header(text_alignment="center", body="Ready to find best stocks?")
    
st.write("")
st.write("")
   
with st.container(horizontal_alignment="center", vertical_alignment="center"):# Example usage of the Team Agent Coordinator
    team_agent = team_agent_coordinator()
    st.title(text_alignment="center", body="Chat with the AI Stock Screener Agent")
    
st.write("")
    
with st.container(horizontal_alignment="center", vertical_alignment="center"):
    # Initialize session state for agent response
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize session_id for agent memory persistence
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())

    # Initialize user_id for memory scoping (can be customized per user)
    if "user_id" not in st.session_state:
        st.session_state.user_id = "default_user"
        
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


