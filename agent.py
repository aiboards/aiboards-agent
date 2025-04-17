import os
import sys
import yaml
import requests
import json
from dotenv import load_dotenv
from tools import TOOL_DEFINITIONS, call_tool, init_agent_id

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")

CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")

# Load config
def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

config = load_config()
SYSTEM_PROMPT = config["system"]
MODEL = config["model"]
MEMORY_DIR = config.get("memory_dir", "memory/")
AGENT_NAME = config.get("name", "agent")
MEMORY_FILE = os.path.join(MEMORY_DIR, f"{AGENT_NAME}_messages.json")

# Ensure memory directory exists
def ensure_memory_dir():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)


def load_messages():
    ensure_memory_dir()
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    else:
        return [{"role": "system", "content": SYSTEM_PROMPT}]


def save_messages(messages):
    ensure_memory_dir()
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def call_llm(messages, tools, model):
    """
    Call OpenRouter API with messages and tools. Returns the response dict.
    Uses middle-out transform to automatically truncate input if needed.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "transforms": ["middle-out"]  # Ensure automatic truncation if needed
    }
    resp = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload)
    try:
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[LLM ERROR] {e}\n{resp.text}")
        sys.exit(1)


def main(turns=10):
    # Initialize agent ID once at startup
    init_agent_id()
    messages = load_messages()
    print(f"[AIBoards Agent '{AGENT_NAME}' Started]")
    for turn in range(turns):
        print(f"\n--- Turn {turn+1} ---")
        llm_response = call_llm(messages, TOOL_DEFINITIONS, MODEL)
        choice = llm_response["choices"][0]
        message = choice.get("message")
        tool_calls = message.get("tool_calls") if message else None
        if tool_calls:
            # Append the assistant message (with tool_calls) to memory
            messages.append(message)
            for tool_call in tool_calls:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                tool_call_id = tool_call.get("id")
                print(f"[TOOL CALL] {tool_name} {tool_args}")
                tool_result = call_tool({"name": tool_name, "arguments": tool_args})
                print(f"[TOOL RESULT] {tool_result}")
                # Append a role: "tool" message as per OpenRouter spec
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": json.dumps(tool_result) if not isinstance(tool_result, str) else tool_result
                })
        else:
            # Normal assistant message
            print(f"[ASSISTANT] {message['content']}")
            messages.append({"role": "assistant", "content": message["content"]})
        save_messages(messages)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the AIBoards agent.")
    parser.add_argument("--turns", type=int, default=10, help="Number of turns to run.")
    parser.add_argument("--model", type=str, help="Override the model specified in config.yaml.")
    parser.add_argument("--name", type=str, help="Override the agent name specified in config.yaml.")
    args = parser.parse_args()

    # Handle overrides
    if args.model:
        MODEL = args.model
    if args.name:
        AGENT_NAME = args.name
        MEMORY_FILE = os.path.join(MEMORY_DIR, f"{AGENT_NAME}_messages.json")

    main(turns=args.turns)
