import asyncio
import os
import uuid
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# Import the root_agent from our application package
from agent_app.agent import root_agent

# --- 1. Load Environment Variables ---
load_dotenv()
# This will load the GOOGLE_API_KEY from the .env file

# --- 2. Explicitly Configure the Session Service ---
# This is the step that `adk web` was doing implicitly.
# We are creating a service that will store sessions in a local SQLite file.
DB_URL = "sqlite:///./sessions.db"
session_service = DatabaseSessionService(db_url=DB_URL)
print(f"✅ Persistent session storage configured at: {DB_URL}")

# --- 3. Explicitly Configure the Runner ---
# We create a Runner instance, telling it which agent to run and which
# session service to use for managing conversation history and state.
APP_NAME = "my_agent_app"  # This must match the app name used in the analysis script
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)
print(f"✅ Runner configured for agent: '{root_agent.name}'")


# --- 4. The Interactive Terminal Loop ---
async def chat_loop():
    """Main loop to handle interactive chat in the terminal."""
    print("\n--- ADK Interactive Terminal ---")
    print("Your conversation will be saved.")
    print("Type 'exit' or 'quit' to end the session.")

    # We'll use a single user and session for this entire run for simplicity
    user_id = "terminal_user_01"
    session_id = f"term_session_{uuid.uuid4()}"

    # Create the session in our database
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    )
    print(f"\nNew session started (ID: {session.id}).")

    while True:
        try:
            # Get user input from the terminal
            user_input = input("\nYou > ")

            if user_input.lower() in ["exit", "quit"]:
                print("Ending session. Goodbye!")
                break

            # Package the user input into ADK's Content format
            user_message = types.Content(role="user", parts=[types.Part(text=user_input)])

            # This is the core call to the ADK Runner
            print("Agent > ", end="", flush=True)
            final_response_text = ""
            async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=user_message):
                # We'll only print the final text response for a clean chat experience
                if event.is_final_response() and event.content and event.content.parts:
                    response_part = event.content.parts[0].text
                    print(response_part, end="", flush=True)
                    final_response_text += response_part
            
            # Print a newline after the agent's full response
            if final_response_text:
                print()

        except (KeyboardInterrupt, EOFError):
            print("\nEnding session. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            continue

if __name__ == "__main__":
    try:
        asyncio.run(chat_loop())
    except Exception as e:
        print(f"Application failed to start: {e}")