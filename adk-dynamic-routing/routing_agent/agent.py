import asyncio
import os
import warnings
from typing import AsyncGenerator, List

from google import genai
from google.adk.agents import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from dotenv import load_dotenv

from .prompts import ROUTING_AGENT_INSTRUCTIONS

load_dotenv()

warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*", category=UserWarning)

client = genai.Client(
    vertexai=True, project=os.getenv('GOOGLE_CLOUD_PROJECT'), location=os.getenv('GOOGLE_CLOUD_LOCATION')
)

class RoutingLlm(BaseLlm):
    """A BaseLlm that dynamically routes requests to different Gemini 2.5 models."""

    async def generate_content_async(
        self, request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        """Inspects the request and routes it to the appropriate model."""
        
        contents: List[types.Content] = []
        for content in request.contents:
            parts = [types.Part(text=part.text) for part in content.parts]
            contents.append(types.Content(parts=parts, role=content.role))

        current_user_message = ""
        for content in reversed(contents):
            if content.role == "user":
                current_user_message = " ".join([part.text for part in content.parts if part.text])
                break
        
        if not current_user_message and contents:
            last_content = contents[-1]
            current_user_message = " ".join([part.text for part in last_content.parts if part.text])

        print(f"Current user message: {current_user_message}")

        if len(current_user_message) > 50:
            model_to_use = "gemini-2.5-pro"
            print(f"\nRouting to POWERFUL model: {model_to_use}")
        else:
            model_to_use = "gemini-2.5-flash"
            print(f"\nRouting to FAST model: {model_to_use}")

        response = await client.aio.models.generate_content(
            model=model_to_use,
            contents=contents,
            config=request.config
        )
        
        yield LlmResponse(content=response.candidates[0].content)


root_agent = Agent(
    name="routing_agent",
    model=RoutingLlm(model=""),  # Model is set dynamically
    instruction=ROUTING_AGENT_INSTRUCTIONS,
)
