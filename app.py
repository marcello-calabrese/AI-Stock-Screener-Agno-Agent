import streamlit as st

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
st.markdown("""
## Welcome to the AI Stock Screener Agno Agent! This application leverages advanced AI capabilities to help you analyze and screen stocks effectively.
""")
# Add some spacing
st.write("")
st.write("")
st.write("") 
st.write("")
 

with st.container(vertical_alignment="top",horizontal_alignment="center"):
    st.image("assets/sphere.jpg", width=300)
    st.header(text_alignment="center", body="Ready to find best stocks?")
   

st.write("Chatbot interface coming soon...")
