from agno.team import Team
from agno.db.sqlite import SqliteDb

from agno.models.openai import OpenAIChat
from dotenv import load_dotenv

from team_instructions.team_agent_coordinator import TEAM_AI_INSTRUCTIONS
from agents import fundamental_analysis_agent, news_sentiment_agent

# Load environment variables

load_dotenv()

# Storage team agent sessions in a SQLite DB
storage_team_agent = SqliteDb(db_file="tmp/team_agent/agent_history.db")

# Define the Team Agent Coordinator

def team_agent_coordinator():
    return Team(
        name="Team Agent Coordinator",
        model=OpenAIChat("gpt-5-mini"),
        description="You are the Team Agent Coordinator for an AI-powered stock analysis system.",
        role="You manage and coordinate multiple specialized agents to provide comprehensive investment analysis and recommendations.",
        instructions=TEAM_AI_INSTRUCTIONS,
        members=[fundamental_analysis_agent(), news_sentiment_agent()],
        db=storage_team_agent,
        add_datetime_to_context=True,
        enable_agentic_state=True,
        num_team_history_runs=3,
        markdown=True,
        stream=True,
    )

# Example usage
# team_agent = team_agent_coordinator()
# prompt= input("Enter your investment analysis query: ")

# response = team_agent.print_response(prompt)