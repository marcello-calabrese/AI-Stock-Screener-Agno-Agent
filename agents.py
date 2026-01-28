from agno.agent import Agent,  RunOutputEvent, RunEvent
from agno.tools.yfinance import YFinanceTools
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat
from agno.db.mongo import MongoDb
from typing import Iterator
import os
#from dotenv import load_dotenv
from agents_instructions.fundamental_analysis_agent_instructions import Fundamental_News_Sentiment_Instructions, Fundamental_News_Sentiment_Output
import streamlit as st



tavily_api_key = st.secrets["TAVILY_API_KEY"]
mongodb_uri = st.secrets["MONGO_DB_URL"] + "&tls=true&tlsAllowInvalidCertificates=true"

# Storage agent sessions in a MongoDB

db = MongoDb(db_url=mongodb_uri)

def ai_stock_analysis_agent(openai_api_key: str):
        return Agent(
        model=OpenAIChat(api_key=openai_api_key, id="gpt-5-mini"),
        name="Fundamental Analysis and News Sentiment Agent",
        description="""You are a comprehensive financial analyst and query agent with access 
        to financial data functions and news sentiment analysis tools.
        Your role is to assist users in making informed investment decisions. 
        Combine your expertise in fundamental analysis with insights from news sentiment 
        to deliver well-rounded investment advice.""",
        role="You are a highly knowledgeable financial analyst and company shares news sentiment analyst.",
        tools= [YFinanceTools(exclude_tools=["get_company_news", "get_technical_indicators"]), TavilyTools(api_key=tavily_api_key)],
        instructions= Fundamental_News_Sentiment_Instructions,
        expected_output= Fundamental_News_Sentiment_Output,
        add_datetime_to_context=True,
        markdown=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=1,
        db=db,
        )

