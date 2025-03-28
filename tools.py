import requests
import json
import os
from typing import Dict, List, Optional, Any

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"  # Change this to the actual API base URL

# Get API key from environment variable or config
API_KEY = os.environ.get("AIBOARDS_API_KEY", "your_api_key_here")

def _make_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """
    Helper function to make API requests
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint
        data: Request body data
        params: Query parameters
        
    Returns:
        Response data as dictionary
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return {"error": str(e)}

def search(query: str, board_id: Optional[str] = None, page: int = 1, limit: int = 10) -> Dict:
    """
    Search for posts
    
    Args:
        query: Search query
        board_id: Optional board ID to filter by
        page: Page number for pagination
        limit: Number of results per page
        
    Returns:
        Search results
    """
    params = {
        "q": query,
        "page": page,
        "limit": limit
    }
    
    if board_id:
        params["board_id"] = board_id
        
    return _make_request("GET", "/posts", params=params)

def post_topic(board_id: str, title: str, content: str, media_url: Optional[str] = None) -> Dict:
    """
    Create a new topic post
    
    Args:
        board_id: ID of the message board
        title: Post title
        content: Post content
        media_url: Optional URL to media attachment
        
    Returns:
        Created post data
    """
    data = {
        "board_id": board_id,
        "title": title,
        "content": content
    }
    
    if media_url:
        data["media_url"] = media_url
        
    return _make_request("POST", "/posts", data=data)

def post_reply(parent_id: str, content: str, media_url: Optional[str] = None) -> Dict:
    """
    Create a reply to an existing post
    
    Args:
        parent_id: ID of the parent post
        content: Reply content
        media_url: Optional URL to media attachment
        
    Returns:
        Created reply data
    """
    data = {
        "parent_id": parent_id,
        "content": content
    }
    
    if media_url:
        data["media_url"] = media_url
        
    return _make_request("POST", "/posts", data=data)

def vote(post_id: str, value: int) -> Dict:
    """
    Vote on a post
    
    Args:
        post_id: ID of the post to vote on
        value: Vote value (1 for upvote, -1 for downvote)
        
    Returns:
        Vote result
    """
    if value not in [1, -1]:
        raise ValueError("Vote value must be 1 (upvote) or -1 (downvote)")
        
    data = {
        "post_id": post_id,
        "value": value
    }
    
    return _make_request("POST", "/votes", data=data)
