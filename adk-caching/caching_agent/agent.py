import asyncio
import hashlib
import os
import warnings
from typing import AsyncGenerator, Dict, List

from google import genai
from google.adk.agents import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from dotenv import load_dotenv

from .prompts import CACHING_AGENT_INSTRUCTIONS

load_dotenv()

warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*", category=UserWarning)

client = genai.Client(
    vertexai=True, project=os.getenv('GOOGLE_CLOUD_PROJECT'), location=os.getenv('GOOGLE_CLOUD_LOCATION')
)

llm_cache: Dict[str, LlmResponse] = {}

def get_request_hash(request: LlmRequest) -> str:
    """Creates a stable hash of the last user message in the request."""
    # Find the last message from the user to use as the cache key
    last_user_message = ""
    for content in reversed(request.contents):
        if content.role == "user":
            last_user_message = "".join(part.text for part in content.parts if part.text)
            break
    return hashlib.md5(last_user_message.encode()).hexdigest()

class CachingLlm(BaseLlm):
    """A BaseLlm that adds a caching layer to a Gemini 2.5 model."""

    async def generate_content_async(
        self, request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        cache_key = get_request_hash(request)

        if cache_key in llm_cache:
            print("\n✅ Cache HIT. Returning stored response.")
            yield llm_cache[cache_key]
            return

        print(f"\n❌ Cache MISS. Calling the underlying model: {self.model}")
        
        contents: List[types.Content] = []
        for content in request.contents:
            parts = [types.Part(text=part.text) for part in content.parts]
            contents.append(types.Content(parts=parts, role=content.role))

        response = await client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=request.config
        )
        llm_response = LlmResponse(content=response.candidates[0].content)

        llm_cache[cache_key] = llm_response
        print("📝 Response cached for future use.")

        yield llm_response


root_agent = Agent(
    name="caching_agent",
    model=CachingLlm(model="gemini-2.5-flash"),
    instruction=CACHING_AGENT_INSTRUCTIONS,
)
