# server.py
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from environment variable (for Cloud Run) or use default
port = int(os.environ.get("PORT", 8050))

# Create an MCP server with SSE transport
mcp = FastMCP("TodoListServer", host="0.0.0.0", port=port)

# Path to store todos (in memory for now, but can be persisted to file)
TODOS_FILE = "todos.json"

# In-memory storage
todos: Dict[str, Dict] = {}

def load_todos():
    """Load todos from file if it exists"""
    global todos
    if os.path.exists(TODOS_FILE):
        try:
            with open(TODOS_FILE, 'r') as f:
                todos = json.load(f)
        except:
            todos = {}

def save_todos():
    """Save todos to file"""
    with open(TODOS_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

# Load todos on startup
load_todos()

@mcp.tool()
def create_todo(title: str, description: str = "", priority: str = "medium") -> str:
    """Create a new todo item
    
    Args:
        title: The title of the todo
        description: Optional description of the todo
        priority: Priority level (low, medium, high)
    
    Returns:
        Success message with the created todo ID
    """
    todo_id = f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(todos)}"
    
    todos[todo_id] = {
        "id": todo_id,
        "title": title,
        "description": description,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    save_todos()
    logger.info(f"Created todo: {todo_id} - {title}")
    return f"Created todo '{title}' with ID: {todo_id}"

@mcp.tool()
def list_todos(filter_by: str = "all") -> str:
    """List all todos with optional filtering
    
    Args:
        filter_by: Filter todos by status - 'all', 'completed', 'pending'
    
    Returns:
        JSON formatted list of todos
    """
    filtered_todos = []
    
    for todo_id, todo in todos.items():
        if filter_by == "all":
            filtered_todos.append(todo)
        elif filter_by == "completed" and todo["completed"]:
            filtered_todos.append(todo)
        elif filter_by == "pending" and not todo["completed"]:
            filtered_todos.append(todo)
    
    # Sort by priority (high -> medium -> low) and creation date
    priority_order = {"high": 0, "medium": 1, "low": 2}
    filtered_todos.sort(key=lambda x: (priority_order.get(x["priority"], 1), x["created_at"]))
    
    if not filtered_todos:
        return f"No todos found with filter: {filter_by}"
    
    # Format the response with clear numbering and IDs
    response = f"Found {len(filtered_todos)} todo(s):\n\n"
    for i, todo in enumerate(filtered_todos, 1):
        status = "✓" if todo["completed"] else "○"
        response += f"{i}. {status} [{todo['priority'].upper()}] {todo['title']}\n"
        if todo["description"]:
            response += f"   Description: {todo['description']}\n"
        response += f"   ID: {todo['id']}\n"
        response += f"   Created: {todo['created_at'][:10]}\n"
        response += f"   To complete this task, use ID: {todo['id']}\n\n"
    
    return response

@mcp.tool()
def get_todo(todo_id: str) -> str:
    """Get details of a specific todo
    
    Args:
        todo_id: The ID of the todo to retrieve
    
    Returns:
        JSON formatted todo details
    """
    if todo_id not in todos:
        logger.error(f"Todo not found: {todo_id}")

        return f"Todo with ID '{todo_id}' not found"
    
    todo = todos[todo_id]
    status = "Completed" if todo["completed"] else "Pending"
    
    response = f"Todo Details:\n"
    response += f"Title: {todo['title']}\n"
    response += f"Description: {todo['description'] or 'No description'}\n"
    response += f"Priority: {todo['priority']}\n"
    response += f"Status: {status}\n"
    response += f"Created: {todo['created_at']}\n"
    response += f"Updated: {todo['updated_at']}\n"
    
    return response

@mcp.tool()
def update_todo(todo_id: str, title: Optional[str] = None, 
                description: Optional[str] = None, 
                priority: Optional[str] = None) -> str:
    """Update an existing todo
    
    Args:
        todo_id: The ID of the todo to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority (optional)
    
    Returns:
        Success message
    """
    if todo_id not in todos:
        logger.error(f"Todo not found: {todo_id}")

        return f"Todo with ID '{todo_id}' not found"
    
    todo = todos[todo_id]
    
    if title is not None:
        todo["title"] = title
    if description is not None:
        todo["description"] = description
    if priority is not None:
        todo["priority"] = priority
    
    todo["updated_at"] = datetime.now().isoformat()
    save_todos()
    
    return f"Updated todo '{todo['title']}' (ID: {todo_id})"

@mcp.tool()
def complete_todo(todo_id: str) -> str:
    """Mark a todo as completed
    
    Args:
        todo_id: The ID of the todo to complete
    
    Returns:
        Success message
    """
    if todo_id not in todos:
        logger.error(f"Todo not found: {todo_id}")

        return f"Todo with ID '{todo_id}' not found"
    
    todo = todos[todo_id]
    if todo["completed"]:
        return f"Todo '{todo['title']}' is already completed"
    
    todo["completed"] = True
    todo["updated_at"] = datetime.now().isoformat()
    save_todos()

    logger.info(f"Completed todo: {todo_id} - {todo['title']}")
    return f"Completed todo '{todo['title']}' (ID: {todo_id})"

@mcp.tool()
def uncomplete_todo(todo_id: str) -> str:
    """Mark a completed todo as pending
    
    Args:
        todo_id: The ID of the todo to mark as pending
    
    Returns:
        Success message
    """
    if todo_id not in todos:
        logger.error(f"Todo not found: {todo_id}")

        return f"Todo with ID '{todo_id}' not found"
    
    todo = todos[todo_id]
    if not todo["completed"]:
        return f"Todo '{todo['title']}' is already pending"
    
    todo["completed"] = False
    todo["updated_at"] = datetime.now().isoformat()
    save_todos()
    
    return f"Marked todo '{todo['title']}' as pending (ID: {todo_id})"

@mcp.tool()
def delete_todo(todo_id: str) -> str:
    """Delete a todo
    
    Args:
        todo_id: The ID of the todo to delete
    
    Returns:
        Success message
    """
    if todo_id not in todos:
        return f"Todo with ID '{todo_id}' not found"
    
    todo_title = todos[todo_id]["title"]
    del todos[todo_id]
    save_todos()
    
    return f"Deleted todo '{todo_title}' (ID: {todo_id})"

@mcp.tool()
def clear_completed_todos() -> str:
    """Delete all completed todos
    
    Returns:
        Success message with count of deleted todos
    """
    completed_ids = [todo_id for todo_id, todo in todos.items() if todo["completed"]]
    
    if not completed_ids:
        return "No completed todos to clear"
    
    for todo_id in completed_ids:
        del todos[todo_id]
    
    save_todos()
    return f"Cleared {len(completed_ids)} completed todo(s)"

@mcp.tool()
def get_todo_stats() -> str:
    """Get statistics about todos
    
    Returns:
        Summary of todo statistics
    """
    total = len(todos)
    completed = sum(1 for todo in todos.values() if todo["completed"])
    pending = total - completed
    
    high_priority = sum(1 for todo in todos.values() if todo["priority"] == "high" and not todo["completed"])
    medium_priority = sum(1 for todo in todos.values() if todo["priority"] == "medium" and not todo["completed"])
    low_priority = sum(1 for todo in todos.values() if todo["priority"] == "low" and not todo["completed"])
    
    stats = f"Todo Statistics:\n"
    stats += f"Total todos: {total}\n"
    stats += f"Completed: {completed}\n"
    stats += f"Pending: {pending}\n\n"
    
    if pending > 0:
        stats += f"Pending by priority:\n"
        stats += f"  High: {high_priority}\n"
        stats += f"  Medium: {medium_priority}\n"
        stats += f"  Low: {low_priority}\n"
    
    return stats

@mcp.tool()
def complete_todo_by_number(position: int) -> str:
    """Complete a todo by its position number in the list
    
    Args:
        position: The position number of the todo (1 for first, 2 for second, etc.)
    
    Returns:
        Success message
    """
    # Get all pending todos
    pending_todos = []
    for todo_id, todo in todos.items():
        if not todo["completed"]:
            pending_todos.append((todo_id, todo))
    
    # Sort by priority and creation date
    priority_order = {"high": 0, "medium": 1, "low": 2}
    pending_todos.sort(key=lambda x: (priority_order.get(x[1]["priority"], 1), x[1]["created_at"]))
    
    # Check if position is valid
    if position < 1 or position > len(pending_todos):
        return f"Invalid position. You have {len(pending_todos)} pending todos. Please use a number between 1 and {len(pending_todos)}."
    
    # Get the todo at the specified position
    todo_id, todo = pending_todos[position - 1]
    
    # Mark as completed
    todo["completed"] = True
    todo["updated_at"] = datetime.now().isoformat()
    save_todos()
    
    return f"Completed todo #{position}: '{todo['title']}' (ID: {todo_id})"

# Run the server
if __name__ == "__main__":
    print(f"Starting Todo List MCP Server on http://0.0.0.0:{port}")
    print(f"The server will be accessible at http://localhost:{port}/sse")
    mcp.run(transport="sse")