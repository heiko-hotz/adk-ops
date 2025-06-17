import os
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from google.adk.sessions.database_session_service import StorageSession

# --- Configuration ---
# This MUST match the configuration used by your other scripts
APP_NAME = "my_agent_app"
DB_URL = "sqlite:///./sessions.db"

def main():
    """
    Connects to the session database, extracts analysis data,
    calculates aggregate metrics, and prints a report to the terminal.
    """
    print("--- Starting Session Analysis Reporting Script ---")

    db_file_path = DB_URL.replace("sqlite:///", "")
    if not os.path.exists(db_file_path):
        print(f"Database file not found at '{db_file_path}'. Please run `python main.py` and `python analysis_script.py` first.")
        return

    # --- 1. Connect to the Database and Fetch Analyzed Sessions ---
    engine = create_engine(DB_URL)
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()

    # Query for all sessions of the app that have the analysis key in their state
    # We use SQLAlchemy's JSON capabilities to query inside the state field.
    # The ->> operator extracts a JSON field as text.
    stmt = select(StorageSession).where(
        StorageSession.app_name == APP_NAME,
        StorageSession.state.op('->>')('post_analysis_v1').isnot(None)
    )
    
    analyzed_sessions = db_session.execute(stmt).scalars().all()
    db_session.close()

    if not analyzed_sessions:
        print("No analyzed sessions found. Please run the `analysis_script.py` first.")
        return

    print(f"\nFound {len(analyzed_sessions)} analyzed sessions to report on.")

    # --- 2. Extract Analysis Data from Each Session ---
    all_analysis_data = []
    for session_record in analyzed_sessions:
        # The 'state' column is a dictionary (or JSONB). We can access it directly.
        analysis_data = session_record.state.get("post_analysis_v1")
        if analysis_data:
            # Add session_id for context in the report
            analysis_data['session_id'] = session_record.id
            all_analysis_data.append(analysis_data)

    # --- 3. Calculate Aggregate Metrics ---
    total_sessions = len(all_analysis_data)
    total_turns = sum(data['turn_count'] for data in all_analysis_data)
    total_duration_seconds = sum(data['duration_seconds'] for data in all_analysis_data)

    average_turns_per_session = round(total_turns / total_sessions, 2) if total_sessions > 0 else 0
    average_duration_per_session = round(total_duration_seconds / total_sessions, 2) if total_sessions > 0 else 0

    # Specialist usage frequency
    specialist_usage = {}
    for data in all_analysis_data:
        for specialist in data.get('used_specialists', []):
            specialist_usage[specialist] = specialist_usage.get(specialist, 0) + 1

    # --- 4. Print the Report to the Terminal ---
    print("\n" + "="*50)
    print(" " * 15 + "SESSION ANALYSIS REPORT")
    print("="*50)
    print(f"Application Name:      {APP_NAME}")
    print(f"Total Analyzed Sessions: {total_sessions}")
    print("-" * 50)
    print("\nAggregate Metrics:")
    print(f"  - Average Turns per Session:    {average_turns_per_session}")
    print(f"  - Average Duration per Session: {average_duration_per_session:.2f} seconds")
    
    if specialist_usage:
        print("\nSpecialist Agent Usage:")
        for specialist, count in specialist_usage.items():
            print(f"  - {specialist:<25} used in {count} session(s)")
    
    print("\n" + "="*50)
    print(" " * 17 + "DETAILED SESSION DATA")
    print("="*50)
    # Print a table header
    print(f"{'Session ID':<38} | {'Turns':<6} | {'Duration (s)':<13} | {'Used Specialists'}")
    print("-" * 80)
    for data in all_analysis_data:
        specialists_str = ", ".join(data.get('used_specialists', ['None']))
        print(f"{data['session_id']:<38} | {data['turn_count']:<6} | {data['duration_seconds']:<13.2f} | {specialists_str}")
    
    print("\n" + "="*50)
    print("--- End of Report ---")


if __name__ == "__main__":
    main()