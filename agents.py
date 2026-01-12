from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

from dotenv import load_dotenv
from agents_instructions.fundamental_analysis_agent_instructions import FundamentalExpectedOutput, FundamentalInstructions
from agents_instructions.news_shares_sentiment_agent_instructions import NewsSentimentExpectedOutput, NewsSentimentInstructions


# Load the environment variables

load_dotenv()

# Storage agent sessions in a SQLite DB
storage_fund_analysis = SqliteDb(db_file="tmp/fund_analysis/agent_history.db")
storage_news_sentiment = SqliteDb(db_file="tmp/news_sentiment/agent_history.db")


## ------------------- Fundamental Analysis Agent ------------------- ##
# Fundamental Analysis Agent with Yahoo Finance Tools

def fundamental_analysis_agent():
    return Agent(
        model=OpenAIChat("gpt-5-mini"),
        name="Fundamental Analysis Agent",
        description="You are a comprehensive fundamental investment analyst with access to financial data functions.",
        role="You are a highly knowledgeable financial analyst specializing in fundamental analysis of stocks",
        tools= [YFinanceTools(exclude_tools=["get_company_news", "get_technical_indicators"])],
        instructions= FundamentalInstructions,
        expected_output= FundamentalExpectedOutput,
        markdown=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=3,
        db=storage_fund_analysis,
        add_datetime_to_context=True,
        stream=True,
        )


# Example usage

# prompt= input("Enter your investment analysis query: ")
# agent = fundamental_analysis_agent()
# response = agent.print_response(prompt)

## ------------------------------------------------------------------------ ##

## ------------------- 5 shares suggested news sentiment agent ------------------- ##

def news_sentiment_agent():
    return Agent(
        model=OpenAIChat("gpt-5-mini"),
        #model=Groq(id="llama-3.3-70b-versatile"),
        name="News Sentiment Analysis Agent",
        role="You are a highly knowledgeable financial analyst specializing in news sentiment analysis for stocks.",
        description="You are an expert in analyzing news sentiment for stock market investments.",
        tools= [TavilyTools()],
        instructions=NewsSentimentInstructions,
        expected_output=NewsSentimentExpectedOutput,
        markdown=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=3,
        db=storage_news_sentiment,
        add_datetime_to_context=True,
        stream=True,
        )
    
# Example usage

# prompt= input("Enter your investment analysis query: ")
# agent = news_sentiment_agent()
# response = agent.print_response(prompt)