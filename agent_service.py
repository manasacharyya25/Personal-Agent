from llm_client import llm_client

async def process_query(user_msg : str, llm_client : llm_client):
    # Create Prompt
    prompt = f"Answer me this {user_msg}"

    # Send Query to LLM
    response = await llm_client.send_message(prompt)

    return response