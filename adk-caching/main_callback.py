import asyncio
import uuid
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types
from caching_agent_callback.agent import root_agent

# Load environment variables from .env file
load_dotenv()

async def main():
    """A minimal, non-interactive test harness for the caching agent with model-level caching."""
    runner = InMemoryRunner(agent=root_agent)
    print("--- Caching Agent Test (Model-Level Caching) ---")

    # Create a single session to be used for the entire conversation
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user_1")

    # --- Test Case 1: First call (should be a cache miss) ---
    print("\n--- First call (cache miss) ---")
    message1 = types.Content(role="user", parts=[types.Part(text="What is the exact speed of light in a vacuum?")])
    print(f"You > {message1.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message1
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

    # --- Test Case 2: Second call with the same text (should be a cache hit) ---
    print("\n--- Second call (cache hit) ---")
    message2 = types.Content(role="user", parts=[types.Part(text="What is the exact speed of light in a vacuum?")])
    print(f"You > {message2.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message2
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

    # --- Test Case 3: Third call with different text (should be a cache miss) ---
    print("\n--- Third call with different text (cache miss) ---")
    message3 = types.Content(role="user", parts=[types.Part(text="What is the value of pi?")])
    print(f"You > {message3.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message3
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

    # --- Test Case 4: Repeat first question (should be a cache hit) ---
    print("\n--- Repeat first question (cache hit) ---")
    message4 = types.Content(role="user", parts=[types.Part(text="What is the exact speed of light in a vacuum?")])
    print(f"You > {message4.parts[0].text}")
    print("Agent >", end="", flush=True)
    async for event in runner.run_async(
        user_id=session.user_id, session_id=session.id, new_message=message4
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(main()) 