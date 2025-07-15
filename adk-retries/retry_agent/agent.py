from google.adk.agents import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google import genai
from google.genai import types
from typing import AsyncGenerator, List
import asyncio
import warnings
from .prompts import RETRY_AGENT_INSTRUCTIONS
from dotenv import load_dotenv
import os
load_dotenv()

# Suppress experimental feature warnings from Google ADK
warnings.filterwarnings("ignore", message=".*EXPERIMENTAL.*", category=UserWarning)

client = genai.Client(
    vertexai=True, project=os.getenv('GOOGLE_CLOUD_PROJECT'), location=os.getenv('GOOGLE_CLOUD_LOCATION')
)

class RetryableLlm(BaseLlm):
    """A BaseLlm implementation that adds retry capabilities to any Gemini model."""
    max_retries: int = 3

    async def generate_content_async(
        self, request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        """Generates content from the Gemini model with retry capabilities."""

        contents: List[types.Content] = []
        for content in request.contents:
            parts = [types.Part(text=part.text) for part in content.parts]
            contents.append(types.Content(parts=parts, role=content.role))

        # Retry loop
        for attempt in range(self.max_retries):
            try:
                if attempt < self.max_retries - 1:
                    print(f"🧪 TESTING: Artificially raising exception on attempt {attempt + 1}")
                    raise Exception(f"Simulated failure for testing - attempt {attempt + 1}")
                
                response = await client.aio.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=request.config
                )
                
                print(f"✅ SUCCESS: Request succeeded on attempt {attempt + 1}")
                
                yield LlmResponse(content=response.candidates[0].content)
                return  # Success, exit the retry loop
                
            except Exception as e:
                if attempt < self.max_retries:
                    print(f"❌ Attempt {attempt + 1} failed: {e}. Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    print(f"💥 All {self.max_retries + 1} attempts failed. Raising last exception.")
                    raise e

root_agent = Agent(
    name="retry_agent",
    model=RetryableLlm(model="gemini-2.5-flash", max_retries=3),
    instruction=RETRY_AGENT_INSTRUCTIONS
) 