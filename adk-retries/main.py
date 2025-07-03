
import asyncio
import uuid
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from retry_agent.agent import root_agent

# Load environment variables from .env file
load_dotenv()

async def main():
    """A minimal, non-interactive test harness for the retry agent."""
    runner = InMemoryRunner(agent=root_agent)
    print("--- Retry Agent Test ---")
    print("The agent is configured to simulate 2 failures before succeeding.")

    # Create a single session for the test
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user_1")

    # --- Run the test call ---
    message = types.Content(role="user", parts=[types.Part(text="Tell me a fun fact about the ocean.")])
    print(f"\nYou > {message.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())

