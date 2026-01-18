from agno.agent import Agent,  RunOutputEvent, RunEvent
from agno.tools.yfinance import YFinanceTools
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from typing import Iterator
from dotenv import load_dotenv
from agents_instructions.fundamental_analysis_agent_instructions import Fundamental_News_Sentiment_Instructions, Fundamental_News_Sentiment_Output



# Load the environment variables

load_dotenv()

# Storage agent sessions in a SQLite DB
storage_fund_analysis = SqliteDb(db_file="tmp/fund_analysis/agent_history.db")


## ------------------- Fundamental Analysis and News Sentiment Single Agent ------------------- ##


# def ai_stock_analysis_agent():
#     return Agent(
#         model=OpenAIChat("gpt-5-mini"),
#         name="Fundamental Analysis and News Sentiment Agent",
#         description="""You are a comprehensive financial analyst and query agent with access 
#         to financial data functions and news sentiment analysis tools.
#         Your role is to assist users in making informed investment decisions. 
#         Combine your expertise in fundamental analysis with insights from news sentiment 
#         to deliver well-rounded investment advice.""",
#         role="You are a highly knowledgeable financial analyst and company shares news sentiment analyst.",
#         tools= [YFinanceTools(exclude_tools=["get_company_news", "get_technical_indicators"]), TavilyTools()],
#         instructions= Fundamental_News_Sentiment_Instructions,
#         expected_output= Fundamental_News_Sentiment_Output,
#         add_datetime_to_context=True,
#         markdown=True,
#         enable_user_memories=True,
#         add_history_to_context=True,
#         num_history_runs=3,
#         db=storage_fund_analysis,
#         stream=True,
#         )

ai_stock_analysis_agent = Agent(
        model=OpenAIChat("gpt-5-mini"),
        name="Fundamental Analysis and News Sentiment Agent",
        description="""You are a comprehensive financial analyst and query agent with access 
        to financial data functions and news sentiment analysis tools.
        Your role is to assist users in making informed investment decisions. 
        Combine your expertise in fundamental analysis with insights from news sentiment 
        to deliver well-rounded investment advice.""",
        role="You are a highly knowledgeable financial analyst and company shares news sentiment analyst.",
        tools= [YFinanceTools(exclude_tools=["get_company_news", "get_technical_indicators"]), TavilyTools()],
        instructions= Fundamental_News_Sentiment_Instructions,
        expected_output= Fundamental_News_Sentiment_Output,
        add_datetime_to_context=True,
        markdown=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=3,
        db=storage_fund_analysis
        
)

# Example usage 1

# prompt= input("Enter your investment analysis query: ")
# agent = ai_stock_analysis_agent()
# response = agent.print_response(prompt)



# Example usage 2 - Streaming response -  to use in web apps such as Streamlit

# prompt = input("Enter your investment analysis query: ")
# # Run agent and return the response as a stream
# stream: Iterator[RunOutputEvent] = ai_stock_analysis_agent.run(prompt, stream=True)
# for chunk in stream:
#     if chunk.event == RunEvent.run_content:
#         print(chunk.content)