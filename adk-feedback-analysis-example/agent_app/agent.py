from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .tools import weather_tool, stock_tool

# --- Specialist Agents ---

# Specialist for weather information
weather_specialist = Agent(
    name="WeatherAgent",
    model="gemini-2.0-flash",
    description="Provides current weather information for a given city.",
    instruction="You are a weather specialist. Use the get_weather tool to answer user queries.",
    tools=[weather_tool],
)

# Specialist for stock information
stock_specialist = Agent(
    name="StockAgent",
    model="gemini-2.0-flash",
    description="Provides current stock price information for a given ticker symbol.",
    instruction="You are a stock market specialist. Use the get_stock_price tool to answer user queries.",
    tools=[stock_tool],
)


# --- Root Agent ---
# This is the main agent the user interacts with.
# It uses the specialist agents as tools to delegate tasks.

root_agent = Agent(
    name="RootFinancialWeatherAssistant",
    model="gemini-2.0-flash",
    description="A helpful assistant that can provide weather and stock information by delegating to specialists.",
    instruction="""
    You are a root assistant. Your job is to understand the user's request and
    delegate to the appropriate specialist tool.

    - If the user asks about weather, use the 'WeatherAgent' tool.
    - If the user asks about stock prices, use the 'StockAgent' tool.

    Present the information returned by the tool clearly to the user.
    """,
    # The RootAgent's tools are the other agents, wrapped in AgentTool
    tools=[
        AgentTool(agent=weather_specialist),
        AgentTool(agent=stock_specialist),
    ]
)