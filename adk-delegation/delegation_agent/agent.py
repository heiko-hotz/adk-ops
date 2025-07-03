from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
load_dotenv()

math_agent = LlmAgent(
    name="math_agent",
    model="gemini-2.5-flash",
    description="A specialist agent that handles all mathematical questions, including arithmetic, algebra, and calculus.",
    instruction=(
        "You are a math expert. Your only purpose is to solve math problems. "
        "Provide clear, step-by-step solutions. Do not answer any non-math questions."
    ),
    # disallow_transfer_to_peers=True,
    # disallow_transfer_to_parent=True,
)

chemistry_agent = LlmAgent(
    name="chemistry_agent",
    model="gemini-2.5-flash",
    description="A specialist agent that handles all chemistry questions, including organic chemistry, inorganic chemistry, and physical chemistry.",
    instruction=(
        "You are a chemistry expert. Your only purpose is to solve chemistry problems. "
        "Provide clear, step-by-step solutions. Do not answer any non-chemistry questions."
    ),
)

root_agent = LlmAgent(
    name="root_agent",
    model="gemini-2.5-flash",
    description="A general-purpose assistant that can delegate tasks to specialists.",
    
    sub_agents=[math_agent, chemistry_agent],
    
    instruction=(
        "You are the main assistant. Your primary job is to determine if a user's request "
        "is a math or chemistry question. \n\n"
        "- If the query is related to mathematics (e.g., 'what is 2+2?', 'solve for x', 'what is a derivative?'), "
        "you MUST immediately transfer the conversation to the 'math_agent'.\n"
        "- If the query is related to chemistry (e.g., 'what is the molecular formula of water?', 'explain chemical bonding', 'balance this equation'), "
        "you MUST immediately transfer the conversation to the 'chemistry_agent'.\n"
        "- To do this, call the `transfer_to_agent(agent_name='math_agent')` or `transfer_to_agent(agent_name='chemistry_agent')` function respectively.\n"
        "- For any other type of question, answer it yourself to the best of your ability."
    )
)