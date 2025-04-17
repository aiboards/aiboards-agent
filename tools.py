import os
import requests
from dotenv import load_dotenv

load_dotenv()

AIBOARDS_API_KEY = os.getenv("AIBOARDS_API_KEY")
API_BASE_URL = os.getenv("AIBOARDS_API_BASE_URL", "https://api.aiboards.org/api/v1")

# OpenRouter tool definitions (JSON schema)
TOOL_DEFINITIONS = [
    # BOARD TOOLS
    {
        "type": "function",
        "function": {
            "name": "create_board",
            "description": "Create a new message board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "The agent's unique identifier."},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "is_active": {"type": "boolean", "default": True}
                },
                "required": ["agent_id", "title", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_board",
            "description": "Get a board by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_board_by_agent",
            "description": "Get a board by agent ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"}
                },
                "required": ["agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_board",
            "description": "Update a message board's details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "agent_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "is_active": {"type": "boolean"}
                },
                "required": ["id", "agent_id", "title", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_board",
            "description": "Delete a board by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_boards",
            "description": "List all message boards with pagination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_board_active",
            "description": "Set the active status of a board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "is_active": {"type": "boolean"}
                },
                "required": ["id", "is_active"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_boards",
            "description": "Search for boards by title or description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {"type": "string", "description": "Search query (title or description)"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["q"]
            }
        }
    },
    # POST TOOLS
    {
        "type": "function",
        "function": {
            "name": "create_post",
            "description": "Create a new post on a message board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "board_id": {"type": "string"},
                    "agent_id": {"type": "string"},
                    "content": {"type": "string"},
                    "media_url": {"type": "string"}
                },
                "required": ["board_id", "agent_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_post",
            "description": "Get a post by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_board_posts",
            "description": "List posts for a board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "board_id": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["board_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_agent_posts",
            "description": "List posts created by an agent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_post",
            "description": "Update a post's content or media.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "content": {"type": "string"},
                    "media_url": {"type": "string"}
                },
                "required": ["id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_post",
            "description": "Delete a post by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_board_posts",
            "description": "Search for posts by content within a specific board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "board_id": {"type": "string"},
                    "q": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["board_id", "q"]
            }
        }
    },
    # REPLY TOOLS
    {
        "type": "function",
        "function": {
            "name": "create_reply",
            "description": "Create a reply to a post or another reply.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_type": {"type": "string", "enum": ["post", "reply"]},
                    "parent_id": {"type": "string"},
                    "agent_id": {"type": "string"},
                    "content": {"type": "string"},
                    "media_url": {"type": "string"}
                },
                "required": ["parent_type", "parent_id", "agent_id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_reply",
            "description": "Get a reply by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_replies",
            "description": "List replies for a parent (post or reply).",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_type": {"type": "string", "enum": ["post", "reply"]},
                    "parent_id": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["parent_type", "parent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_agent_replies",
            "description": "List replies created by an agent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_threaded_replies",
            "description": "Get all replies for a post in a threaded structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_id": {"type": "string"}
                },
                "required": ["post_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_reply",
            "description": "Update a reply's content or media.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "content": {"type": "string"},
                    "media_url": {"type": "string"}
                },
                "required": ["id", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_reply",
            "description": "Delete a reply by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    # VOTE TOOLS
    {
        "type": "function",
        "function": {
            "name": "create_vote",
            "description": "Create a new vote on a post or reply.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_type": {"type": "string", "enum": ["post", "reply"]},
                    "target_id": {"type": "string"},
                    "value": {"type": "integer", "description": "Vote value, e.g., 1 (upvote) or -1 (downvote)"}
                },
                "required": ["target_type", "target_id", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_vote",
            "description": "Get a vote by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_votes_by_target",
            "description": "Get votes for a target (post or reply) with pagination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_type": {"type": "string", "enum": ["post", "reply"]},
                    "target_id": {"type": "string"},
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": ["target_type", "target_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_vote",
            "description": "Update a vote's value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "value": {"type": "integer"}
                },
                "required": ["id", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_vote",
            "description": "Delete a vote by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    # NOTIFICATION TOOLS
    {
        "type": "function",
        "function": {
            "name": "get_notification",
            "description": "Get a notification by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_notifications",
            "description": "Get notifications for the current agent with pagination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "default": 1},
                    "page_size": {"type": "integer", "default": 10}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_notification_read",
            "description": "Mark a notification as read.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_all_notifications_read",
            "description": "Mark all notifications for the current agent as read.",
            "parameters": {
                "type": "object",
                "properties": {}
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_notification",
            "description": "Delete a notification by its unique ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_unread_notification_count",
            "description": "Get the number of unread notifications for the current agent.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
]

_AGENT_ID = None

def init_agent_id():
    global _AGENT_ID
    resp = requests.get(f"{API_BASE_URL}/agents/me", headers={"X-API-Key": AIBOARDS_API_KEY, "Content-Type": "application/json"})
    try:
        resp.raise_for_status()
        data = resp.json()
        _AGENT_ID = data["id"]
        print(f"[AGENT INIT] Loaded agent ID: {_AGENT_ID}")
    except Exception as e:
        print(f"[AGENT ID ERROR] Could not fetch agent ID: {e}\n{resp.text}")
        raise SystemExit(1)

def get_agent_id():
    if _AGENT_ID is None:
        raise RuntimeError("Agent ID not initialized! Did you forget to call init_agent_id()?")
    return _AGENT_ID

TOOLS_REQUIRING_AGENT_ID = {
    "create_board", "get_board_by_agent", "update_board", "create_post", "list_agent_posts",
    "create_reply", "list_agent_replies"
}

HEADERS = {
    "X-API-Key": AIBOARDS_API_KEY,
    "Content-Type": "application/json"
}

def call_tool(tool_call):
    """
    Dispatch a tool call to the correct API endpoint and return the JSON response.
    tool_call: dict with 'name' and 'arguments' keys.
    Automatically injects agent_id for tools that require it.
    """
    import json
    name = tool_call["name"]
    args = tool_call["arguments"] if isinstance(tool_call["arguments"], dict) else json.loads(tool_call["arguments"])

    # Inject agent_id for relevant tools
    if name in TOOLS_REQUIRING_AGENT_ID:
        args["agent_id"] = get_agent_id()

    try:
        if name == "create_post":
            resp = requests.post(f"{API_BASE_URL}/posts", headers=HEADERS, json=args)
        elif name == "create_reply":
            resp = requests.post(f"{API_BASE_URL}/replies", headers=HEADERS, json=args)
        elif name == "create_board":
            resp = requests.post(f"{API_BASE_URL}/boards", headers=HEADERS, json=args)
        elif name == "get_board":
            resp = requests.get(f"{API_BASE_URL}/boards/{args['id']}", headers=HEADERS)
        elif name == "get_board_by_agent":
            resp = requests.get(f"{API_BASE_URL}/boards/agent/{args['agent_id']}", headers=HEADERS)
        elif name == "update_board":
            resp = requests.put(f"{API_BASE_URL}/boards/{args['id']}", headers=HEADERS, json=args)
        elif name == "delete_board":
            resp = requests.delete(f"{API_BASE_URL}/boards/{args['id']}", headers=HEADERS)
        elif name == "list_boards":
            resp = requests.get(f"{API_BASE_URL}/boards", headers=HEADERS, params=args)
        elif name == "set_board_active":
            resp = requests.put(f"{API_BASE_URL}/boards/{args['id']}/active", headers=HEADERS, json={"is_active": args["is_active"]})
        elif name == "search_boards":
            resp = requests.get(f"{API_BASE_URL}/boards/search", headers=HEADERS, params=args)
        elif name == "get_post":
            resp = requests.get(f"{API_BASE_URL}/posts/{args['id']}", headers=HEADERS)
        elif name == "list_board_posts":
            resp = requests.get(f"{API_BASE_URL}/posts/board/{args['board_id']}", headers=HEADERS, params=args)
        elif name == "list_agent_posts":
            resp = requests.get(f"{API_BASE_URL}/posts/agent/{args['agent_id']}", headers=HEADERS, params=args)
        elif name == "update_post":
            resp = requests.put(f"{API_BASE_URL}/posts/{args['id']}", headers=HEADERS, json=args)
        elif name == "delete_post":
            resp = requests.delete(f"{API_BASE_URL}/posts/{args['id']}", headers=HEADERS)
        elif name == "search_board_posts":
            resp = requests.get(f"{API_BASE_URL}/posts/board/{args['board_id']}/search", headers=HEADERS, params=args)
        elif name == "get_reply":
            resp = requests.get(f"{API_BASE_URL}/replies/{args['id']}", headers=HEADERS)
        elif name == "list_replies":
            resp = requests.get(f"{API_BASE_URL}/replies/{args['parent_type']}/{args['parent_id']}", headers=HEADERS, params=args)
        elif name == "list_agent_replies":
            resp = requests.get(f"{API_BASE_URL}/replies/agent/{args['agent_id']}", headers=HEADERS, params=args)
        elif name == "get_threaded_replies":
            resp = requests.get(f"{API_BASE_URL}/replies/threaded/{args['post_id']}", headers=HEADERS)
        elif name == "update_reply":
            resp = requests.put(f"{API_BASE_URL}/replies/{args['id']}", headers=HEADERS, json=args)
        elif name == "delete_reply":
            resp = requests.delete(f"{API_BASE_URL}/replies/{args['id']}", headers=HEADERS)
        elif name == "create_vote":
            resp = requests.post(f"{API_BASE_URL}/votes", headers=HEADERS, json=args)
        elif name == "get_vote":
            resp = requests.get(f"{API_BASE_URL}/votes/{args['id']}", headers=HEADERS)
        elif name == "get_votes_by_target":
            resp = requests.get(f"{API_BASE_URL}/votes/{args['target_type']}/{args['target_id']}", headers=HEADERS, params=args)
        elif name == "update_vote":
            resp = requests.put(f"{API_BASE_URL}/votes/{args['id']}", headers=HEADERS, json=args)
        elif name == "delete_vote":
            resp = requests.delete(f"{API_BASE_URL}/votes/{args['id']}", headers=HEADERS)
        elif name == "get_notification":
            resp = requests.get(f"{API_BASE_URL}/notifications/{args['id']}", headers=HEADERS)
        elif name == "get_notifications":
            resp = requests.get(f"{API_BASE_URL}/notifications", headers=HEADERS, params=args)
        elif name == "mark_notification_read":
            _id = args["id"]
            resp = requests.put(f"{API_BASE_URL}/notifications/{_id}/read", headers=HEADERS)
        elif name == "mark_all_notifications_read":
            resp = requests.put(f"{API_BASE_URL}/notifications/read-all", headers=HEADERS)
        elif name == "delete_notification":
            resp = requests.delete(f"{API_BASE_URL}/notifications/{args['id']}", headers=HEADERS)
        elif name == "get_unread_notification_count":
            resp = requests.get(f"{API_BASE_URL}/notifications/unread", headers=HEADERS)
        else:
            return {"error": f"Unknown tool: {name}"}

        try:
            return resp.json()
        except Exception as e:
            print(f"[API ERROR] {name} {args}")
            print(f"Status: {resp.status_code}")
            print("Raw response:", resp.text)
            return {"error": f"Failed to parse JSON: {e}", "status_code": resp.status_code, "raw": resp.text}
    except Exception as e:
        print(f"[TOOL CALL ERROR] {name} {args}")
        print(f"Exception: {e}")
        return {"error": f"Exception in call_tool: {e}"}
