import asyncio
import hashlib
import json
import os
import warnings
from typing import Any, Dict, Optional

from google import genai
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from dotenv import load_dotenv

from .prompts import CACHING_AGENT_INSTRUCTIONS

load_dotenv()

warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*", category=UserWarning)

# Cache for demonstration purposes (currently unused but ready for tools)
tool_cache: Dict[str, Any] = {}

def create_cache_key(tool_name: str, args: Dict[str, Any]) -> str:
    """Creates a stable, unique cache key from the tool name and args."""
    args_string = json.dumps(args, sort_keys=True) if args else "{}"
    return f"cache:tool:{tool_name}:{args_string}"

def before_tool_cache_check(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """Checks the cache before a tool runs."""
    cache_key = create_cache_key(tool.name, args)
    
    if cache_key in tool_cache:
        print(f"\n✅ Cache HIT. Found result for '{tool.name}' in cache. Skipping tool execution.")
        return tool_cache[cache_key]
    
    print(f"\n❌ Cache MISS. No result for '{tool.name}' in cache. Executing tool.")
    return None

def after_tool_cache_populate(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    """Populates the cache after a tool runs."""
    cache_key = create_cache_key(tool.name, args)
    
    tool_cache[cache_key] = tool_response
    print("📝 Tool result cached for future use.")
    
    return None

root_agent = Agent(
    name="caching_agent_callback",
    model="gemini-2.5-flash",
    instruction=CACHING_AGENT_INSTRUCTIONS,
    # Callback architecture ready for tools (currently no tools)
    before_tool_callback=before_tool_cache_check,
    after_tool_callback=after_tool_cache_populate,
)