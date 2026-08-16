from llm_client import llm_client
from tools import TOOLS

async def process_query(user_msg : str, llm_client : llm_client):
    # Create Prompt
    prompt = f"""
    #SYSTEM PROMPT
    You are an AI agent.

    Analyze the user's request and decide what action
    should be taken using the available tools.

    For now, do not execute any tools.
    Simply explain what you have decided to do.

    Here's the set of tools you can use
    {TOOLS}

    If you decide to use a tool, respond ONLY with JSON:
    
        {{
        "tool": "tool_name",
            "arguments": {{
                ...
            }}
        }}

    #USER QUERY
    {user_msg}
    """

    # Send Query to LLM
    response = await llm_client.send_message(prompt)

    return response