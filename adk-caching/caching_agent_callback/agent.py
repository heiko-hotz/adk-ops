import asyncio
import json
import time
from typing import Any, Dict, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part


def get_stock_price(symbol: str) -> dict:
    """
    Simulates a slow API call to fetch a stock price.
    We add a print statement to see when it's actually running.
    """
    print(f"\n---> [Executing Tool] Calling slow external API for stock: {symbol}...")
    time.sleep(2)  # Simulate network latency
    
    # Mock data
    prices = {"GOOGL": 175.57, "MSFT": 444.85}
    price = prices.get(symbol.upper())

    if price:
        return {"status": "success", "symbol": symbol.upper(), "price": price}
    else:
        return {"status": "error", "message": f"Symbol '{symbol}' not found."}


def create_cache_key(tool_name: str, args: Dict[str, Any]) -> str:
    """Creates a stable, unique cache key from the tool name and args."""
    # Use a prefix and serialize args to a stable JSON string
    args_string = json.dumps(args, sort_keys=True)
    return f"cache:tool:{tool_name}:{args_string}"


def before_tool_cache_check(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Checks the cache before a tool runs."""
    cache_key = create_cache_key(tool.name, args)
    
    if cache_key in tool_context.state:
        print(f"--- [CACHE HIT] Found result for '{tool.name}' in cache. Skipping tool execution.")
        cached_result = tool_context.state[cache_key]
        return cached_result  # Return the cached result to skip the tool
    
    print(f"--- [CACHE MISS] No result for '{tool.name}' in cache. Executing tool.")
    return None  # Allow the tool to run normally


def after_tool_cache_populate(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Populates the cache after a tool runs."""
    cache_key = create_cache_key(tool.name, args)
    
    # Store the result in the session state for future use
    tool_context.state[cache_key] = tool_response
    print(f"--- [CACHE POPULATE] Stored result for '{tool.name}' in cache.")
    
    return None # Don't modify the response, just let it pass through



root_agent = Agent(
    model="gemini-2.5-flash",
    name="stock_price_agent",
    instruction="You are a stock price assistant. Use the 'get_stock_price' tool to fetch prices.",
    tools=[get_stock_price],
    # Assign the callbacks
    before_tool_callback=before_tool_cache_check,
    after_tool_callback=after_tool_cache_populate,
)