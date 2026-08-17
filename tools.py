TOOLS = [
    {
        "type": "function",
        "name": "get_new_creators",
        "description": "Get creators scraped today who have not yet been contacted.",
        "parameters": {
            "type": "object",
            "properties": {
                "today_date": {
                    "type": "string",
                    "description": "The date to use when finding newly scraped creators."
                }
            },
            "required": ["today_date"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_rhoq_info",
        "description": "Get information about the RhoQ platform from the knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The question or information to look up about RhoQ."
                }
            },
            "required": ["query"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_previous_message",
        "description": "Find previous messages sent by me that are similar to the current message.",
        "parameters": {
            "type": "object",
            "properties": {
                "current_message": {
                    "type": "string",
                    "description": "The current message to use when finding similar previous messages."
                }
            },
            "required": ["current_message"],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "draft_new_message",
        "description": "Draft a new message for onboarding a creator to the RhoQ platform.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "draft_reply",
        "description": "Draft a reply to an incoming message. It helps to create a response similar to the tone and vocabulary of the admin",
        "parameters": {
            "type": "object",
            "properties": {
                "current_message": {
                    "type": "string",
                    "description": "The incoming message that needs a reply."
                }
            },
            "required": ["current_message"],
            "additionalProperties": False
        },
        "strict": True
    }
]

def get_new_creators(today_date):
    print(f"Searching new creators for {today_date}")
    print(f"Found 10 creators")
    print(f"Finished searching")
    return "10 creators found"

def get_rhoq_info(query):
    print(f"Searching RhoQ Information relevant to {query}")
    return "RhoQ pricing plan : 10$ monthly, 100$ yearly"

def get_previous_message(current_message):
    print(f"Searching previous message similar to {current_message}")
    return "Previous Message"

def draft_new_messaeg():
    return "New Message : Hi how are you"

def draft_reply(current_message):
    print(f"Drafting message for : {current_message}")
    return "Hi here is the info you requested"

TOOL_REGISTRY = {
    "get_new_creators": get_new_creators,
    "get_rhoq_info": get_rhoq_info,
    "get_previous_message": get_previous_message,
    "draft_new_message": draft_new_messaeg,
    "draft_reply": draft_reply
}