import asyncio
import os
from google.adk.sessions import DatabaseSessionService, Session
from google.adk.events import Event, EventActions
from google.genai import types

# --- Configuration ---
# This MUST match the configuration used by the `adk web` command
APP_NAME = "my_agent_app"
DB_URL = "sqlite:///./sessions.db"

# --- Analysis Logic ---
def analyze_session(session: Session) -> dict:
    """Performs analysis on a single session and returns the results."""
    print(f"-> Analyzing session: {session.id} for user: {session.user_id}")

    # Count turns by counting user-authored events
    turn_count = sum(1 for event in session.events if event.author == 'user')

    # Calculate session duration
    first_event_ts = session.events[0].timestamp if session.events else 0
    last_event_ts = session.events[-1].timestamp if session.events else 0
    duration_seconds = round(last_event_ts - first_event_ts, 2)

    # Identify which specialist agents were used
    used_specialists = list(set(
        event.author for event in session.events
        if event.author in ["WeatherAgent", "StockAgent"]
    ))

    analysis_results = {
        "turn_count": turn_count,
        "duration_seconds": duration_seconds,
        "used_specialists": used_specialists,
        "analysis_timestamp": session.last_update_time # Record when analysis was run
    }

    print(f"   -> Analysis complete: {analysis_results}")
    return analysis_results

# --- Data Persistence Logic ---
async def append_analysis_to_session(session_service: DatabaseSessionService, session: Session, analysis_data: dict):
    """Appends analysis results to a session by creating and saving a new event."""
    print(f"-> Appending analysis to session {session.id}...")

    # The analysis results are a state change, stored under a specific key.
    state_delta_for_analysis = {
        "post_analysis_v1": analysis_data
    }

    analysis_event = Event(
        author="analysis_bot",
        invocation_id=f"analysis_{session.id}",
        actions=EventActions(state_delta=state_delta_for_analysis),
        content=types.Content(parts=[types.Part(text=f"Post-session analysis completed.")])
    )

    await session_service.append_event(session=session, event=analysis_event)
    print(f"   -> Successfully appended analysis for session {session.id}.")

# --- Main Execution ---
async def main():
    print("--- Starting Post-Hoc Session Analysis Script ---")

    if not os.path.exists(DB_URL.replace("sqlite:///", "")):
        print(f"Database file not found at '{DB_URL}'. Please run the `adk web` command first to generate sessions.")
        return

    session_service = DatabaseSessionService(db_url=DB_URL)

    # In a real system, you might list all users. For this example, we assume we know them.
    # We will get all sessions for all users of this app.
    list_response = await session_service.list_sessions(app_name=APP_NAME, user_id="terminal_user_01")

    if not list_response.sessions:
        print(f"No sessions found for app '{APP_NAME}' and user 'terminal_user_01'.")
        return

    print(f"Found {len(list_response.sessions)} sessions to process.")
    sessions_analyzed = 0

    for session_summary in list_response.sessions:
        full_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=session_summary.user_id,
            session_id=session_summary.id
        )

        # Check if analysis has already been performed to avoid re-processing
        if "post_analysis_v1" in full_session.state:
            print(f"Session {full_session.id} already analyzed. Skipping.")
            continue

        if not full_session.events:
            print(f"Session {full_session.id} has no events. Skipping.")
            continue

        results = analyze_session(full_session)
        await append_analysis_to_session(session_service, full_session, results)
        sessions_analyzed += 1

    print(f"\n--- Analysis Complete. Processed {sessions_analyzed} new sessions. ---")

if __name__ == "__main__":
    asyncio.run(main())