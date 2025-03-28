import os
import argparse
import json
from agent import Agent
import tools

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="AI Boards Agent")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config file")
    parser.add_argument("--agent-name", type=str, default="aiboards_agent", help="Name of the agent")
    parser.add_argument("--api-key", type=str, help="OpenRouter API key (overrides env variable)")
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENROUTER_API_KEY"] = args.api_key
    
    # Initialize agent
    agent = Agent(agent_name=args.agent_name)
    
    # Load config and run agent
    agent.load_config(args.config)
    agent.run()
    
    print("Agent is ready to process messages")
    
    # Example of how to use the agent with tools
    # Uncomment and modify as needed
    """
    # Example: Search for posts
    search_result = tools.search(query="AI ethics")
    print(f"Search results: {json.dumps(search_result, indent=2)}")
    
    # Add user message
    agent.add_message("user", "What are your thoughts on AI ethics?")
    
    # Get agent response
    response = agent.get_action()
    if "choices" in response and len(response["choices"]) > 0:
        message = response["choices"][0]["message"]
        print(f"Agent response: {message['content']}")
        
        # Add assistant message to conversation
        agent.add_message("assistant", message["content"])
        
        # Save updated trajectory
        agent.save_trajectory()
    """

if __name__ == "__main__":
    main()
