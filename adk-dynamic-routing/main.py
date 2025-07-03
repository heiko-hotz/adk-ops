import asyncio
import uuid
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from routing_agent.agent import root_agent

# Load environment variables from .env file, which is critical for the client
load_dotenv()

async def main():
    """A minimal, non-interactive test harness for the routing agent."""
    runner = InMemoryRunner(agent=root_agent)
    print("--- Dynamic Routing Agent Test ---")

    # --- Test Case 1: Short prompt (should use fast model) ---
    print("\n--- Testing with short prompt ---")
    session1 = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user_1")
    # Correctly create the message with role="user"
    short_message = types.Content(role="user", parts=[types.Part(text="What is the capital of France?")])
    print(f"You > {short_message.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session1.user_id, session_id=session1.id, new_message=short_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

    # --- Test Case 2: Long prompt (should use powerful model) ---
    print("\n--- Testing with long prompt ---")
    session2 = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user_2")
    long_prompt = "Explain the theory of general relativity in simple terms, covering the main concepts like spacetime, gravity as curvature, and the role of mass-energy. Please provide an analogy."
    # Correctly create the message with role="user"
    long_message = types.Content(role="user", parts=[types.Part(text=long_prompt)])
    print(f"You > {long_message.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session2.user_id, session_id=session2.id, new_message=long_message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main())