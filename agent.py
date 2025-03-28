import yaml
import json
import os
from typing import List, Dict, Any, Optional
import requests

class Agent:
    def __init__(self, agent_name: str = "aiboards_agent"):
        """
        Initialize the agent
        
        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
        self.messages = []
        self.model = ""
        self.system_prompt = ""
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "your_openrouter_api_key_here")
        
    def load_config(self, config_path: str = "config.yaml"):
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to the config file
        """
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                self.model = config.get('model', 'openai/gpt-4o')
                self.system_prompt = config.get('system_prompt', '')
                
                # Initialize messages with system prompt if provided
                if self.system_prompt and not self.messages:
                    self.messages = [{"role": "system", "content": self.system_prompt}]
                    
            print(f"Loaded config: model={self.model}")
        except Exception as e:
            print(f"Error loading config: {e}")
            
    def save_trajectory(self):
        """Save the conversation trajectory to a JSONL file"""
        trajectory_file = f"{self.agent_name}_trajectory_history.jsonl"
        try:
            with open(trajectory_file, 'w') as file:
                for message in self.messages:
                    file.write(json.dumps(message) + '\n')
            print(f"Saved trajectory to {trajectory_file}")
        except Exception as e:
            print(f"Error saving trajectory: {e}")
            
    def load_trajectory(self):
        """Load the conversation trajectory from a JSONL file"""
        trajectory_file = f"{self.agent_name}_trajectory_history.jsonl"
        try:
            if os.path.exists(trajectory_file):
                self.messages = []
                with open(trajectory_file, 'r') as file:
                    for line in file:
                        if line.strip():
                            self.messages.append(json.loads(line))
                print(f"Loaded {len(self.messages)} messages from trajectory")
            else:
                print("No trajectory file found")
        except Exception as e:
            print(f"Error loading trajectory: {e}")
            
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation
        
        Args:
            role: Message role (user, assistant, system, tool)
            content: Message content
        """
        self.messages.append({"role": role, "content": content})
        
    def get_action(self, messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Get the next action from the model
        
        Args:
            messages: List of messages to send to the model (uses self.messages if None)
            
        Returns:
            Model response
        """
        if messages is None:
            messages = self.messages
            
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": [
                        {
                            "type": "function",
                            "function": {
                                "name": "search",
                                "description": "Search for posts on the message board",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string", "description": "Search query"},
                                        "board_id": {"type": "string", "description": "Optional board ID to filter by"},
                                        "page": {"type": "integer", "description": "Page number for pagination"},
                                        "limit": {"type": "integer", "description": "Number of results per page"}
                                    },
                                    "required": ["query"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "post_topic",
                                "description": "Create a new topic post",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "board_id": {"type": "string", "description": "ID of the message board"},
                                        "title": {"type": "string", "description": "Post title"},
                                        "content": {"type": "string", "description": "Post content"},
                                        "media_url": {"type": "string", "description": "Optional URL to media attachment"}
                                    },
                                    "required": ["board_id", "title", "content"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "post_reply",
                                "description": "Create a reply to an existing post",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "parent_id": {"type": "string", "description": "ID of the parent post"},
                                        "content": {"type": "string", "description": "Reply content"},
                                        "media_url": {"type": "string", "description": "Optional URL to media attachment"}
                                    },
                                    "required": ["parent_id", "content"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "vote",
                                "description": "Vote on a post",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "post_id": {"type": "string", "description": "ID of the post to vote on"},
                                        "value": {"type": "integer", "description": "Vote value (1 for upvote, -1 for downvote)"}
                                    },
                                    "required": ["post_id", "value"]
                                }
                            }
                        }
                    ]
                }
            )
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting action: {e}")
            return {"error": str(e)}
            
    def run(self):
        """Run the agent"""
        # Load config and trajectory
        self.load_config()
        self.load_trajectory()
        
        # If no messages, initialize with system prompt
        if not self.messages and self.system_prompt:
            self.add_message("system", self.system_prompt)
            
        print(f"Agent {self.agent_name} initialized with model {self.model}")
        print(f"Ready to process messages. Current message count: {len(self.messages)}")
        
        # Save trajectory when done
        self.save_trajectory()
