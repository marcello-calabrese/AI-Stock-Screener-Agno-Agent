import streamlit as st
import uuid
from agno.agent import RunEvent
from dotenv import load_dotenv

with st.sidebar:
        # Open AI API Key input
        st.markdown("# API Configuration")
        openai_api_key = st.text_input(key="openai_api_key", 
        label="Enter your OpenAI API Key:",
        type="password",
        help="Your personal OpenAI API key. This is required to use the stock screener.")
        st.caption("Your API key is not stored and is only used for this session.")

# Cache the agent (created only once, not on every rerun)
@st.cache_resource
def get_agent(_api_key: str):
    from agents import ai_stock_analysis_agent
    return ai_stock_analysis_agent(openai_api_key=_api_key)

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


### Streamlit APP Header ###

st.set_page_config(
    page_title="AI Stock Screener Agno Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AI Stock Screener Agno Agent")
st.header("Welcome to the AI Stock Screener Agent! This application leverages advanced AI capabilities to screen stocks effectively.")
# Add some spacing
st.write("")
st.subheader("The AI Stock Screener Agent combines fundamental analysis and news sentiment to help you make informed investment decisions.")
st.warning("Before you start, please ensure you have your OpenAI API Key ready. Enter it in the sidebar to unlock the full potential of the AI Stock Screener Agent.") 
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
            
    
    # Check if API key is provided
    
    if not openai_api_key:
        st.warning("Please enter your OpenAI API Key in the sidebar to use the AI Stock Screener Agent.")
    else:
        # Get the agent
        agent = get_agent(openai_api_key)
        st.markdown(body="### Ask the AI Stock Screener Agent anything about stock fundamental analysis and news sentiment!", text_alignment="center")
    # Handle user input
        if prompt := st.chat_input(placeholder="Example: Ask the AI stock screener to suggest 5 stocks to invest in the US market."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message in chat
            with st.chat_message("user"):
                st.markdown(prompt)
                
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Generating response... It may take couple of minutes..."):
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
                    
    # Sidebar with Open AI API KEY input and session info
    with st.sidebar:
       
        # Session Information and restart new sessions        
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


