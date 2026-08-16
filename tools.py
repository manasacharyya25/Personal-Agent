TOOLS = [
    # READING TOOLS
    {
        "name": "get_new_creators",
        "description": "Get list of creators scraped today by bot and have not been contacted",
        "parameters": [
            {
                "name":"today_date",
                "type":"string",
                "description": "Today date to consider or newly scraped data",
                "required": True
            }
        ]
    },
    {
        "name": "get_rhoq_info",
        "description": "Get information about RhoQ Platform from Knowledge Base",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "User Query that needs to be answered based on Information about RHoQ",
                "required": True
            }
        ],
        "required": ["query"]
    },
    {
        "name": "get_previous_message",
        "description": "Get previous chat messages made by me, which are similar to current message",
        "parameters": [
            {
                "name": "curr_message",
                "type": "string",
                "description": "Current message against which previous chat response is to be found",
                "required": True
            }
        ],
        "required": ["curr_message"]
    },
    # DRAFT TOOLS
    {
        "name": "draft_new_message",
        "description": "Draft a new message to onboard creator to RhoQ Platform",
        "parameters": []
    },
    {
        "name": "draft_reply",
        "description": "Draft a reply to incoming message",
        "parameters": [
            {
                "name": "curr_message",
                "type": "string",
                "description": "Current message to which reply needs to be drafted",
                "required": True
            }
        ],
        "required": ["curr_message"]
    }
]