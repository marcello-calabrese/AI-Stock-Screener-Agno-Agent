from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools
from agno.tools.tavily import TavilyTools
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.models.groq import Groq
from dotenv import load_dotenv
from agents_instructions.fundamental_analysis_agent_instructions import FundamentalExpectedOutput, FundamentalInstructions


# Load the environment variables

load_dotenv()

# Storage agent sessions in a SQLite DB
storage = SqliteDb(db_file="tmp/agent_history.db")

# Fundamental Analysis Agent with Yahoo Finance Tools

def fundamental_analysis_agent():
    agent = Agent(
        #model=OpenAIChat("gpt-5-mini"),
        model=Groq(id="llama-3.3-70b-versatile"),
        description="You are a comprehensive fundamental investment analyst with access to financial data functions.",
        tools= [YFinanceTools(exclude_tools=["get_company_news", "get_technical_indicators"])],
        name="Fundamental Analysis Agent",
        instructions= FundamentalInstructions,
        expected_output= FundamentalExpectedOutput,
        markdown=True,
        enable_user_memories=True,
        add_history_to_context=True,
        num_history_runs=3,
        db=storage,
        compress_tool_results=True,
        stream=True,
        )
    return agent

prompt= input("Enter your investment analysis query: ")
agent = fundamental_analysis_agent()
response = agent.print_response(prompt)