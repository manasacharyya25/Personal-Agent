from llm_client import llm_client
from tools import TOOLS, TOOL_REGISTRY
import json

async def process_query(user_msg : str, llm_client : llm_client):
    # Create Prompt
    system_prompt = f"""
    You are an AI agent.

    Analyze the user's request and decide what action
    should be taken using the available tools.
    """

    # Send 1st Query to LLM to decide tool call chain
    response = await llm_client.send_message(system_prompt, user_msg, TOOLS)

    # Print the Tool Call Plan provided by LLM
    for item in response.output:
        if item.type == "function_call":
            print(item.name)

    
    # while a final response is received, keep executing tool_call and querying llm
    while True:
        # Execute tool calls
        tool_results = []
    
        for item in response.output:
            if item.type == "function_call":
                call_id = item.call_id
                tool_name = item.name
                tool_args = json.loads(item.arguments)
                tool = TOOL_REGISTRY[tool_name]
                tool_res = tool(**tool_args)
    
                tool_results.append({
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(tool_res)
                })
    
        if not tool_results:
            return response.output_text
        
        response = await llm_client.send_subsequent_message(response.id, tool_results)