# client.py
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def test_todo_server():
    """Test the Todo List MCP Server"""
    
    try:
        # Connect to the server using SSE
        async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                
                print("Connected to Todo List MCP Server!")
                print("=" * 50)
                
                # List available tools
                tools_result = await session.list_tools()
                print("\nAvailable tools:")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                print("\n" + "=" * 50)
                print("\nTesting Todo List Operations:")
                print("=" * 50)
                
                # 1. Create some todos
                print("\n1. Creating todos...")
                
                result1 = await session.call_tool(
                    "create_todo", 
                    arguments={
                        "title": "Complete MCP server implementation",
                        "description": "Finish building the todo list MCP server with all CRUD operations",
                        "priority": "high"
                    }
                )
                print(f"   {result1.content[0].text}")
                
                result2 = await session.call_tool(
                    "create_todo", 
                    arguments={
                        "title": "Write documentation",
                        "description": "Create README and usage examples",
                        "priority": "medium"
                    }
                )
                print(f"   {result2.content[0].text}")
                
                result3 = await session.call_tool(
                    "create_todo", 
                    arguments={
                        "title": "Buy groceries",
                        "priority": "low"
                    }
                )
                print(f"   {result3.content[0].text}")
                
                # 2. List all todos
                print("\n2. Listing all todos...")
                result = await session.call_tool("list_todos", arguments={"filter_by": "all"})
                print(result.content[0].text)
                
                # 3. Get todo stats
                print("\n3. Getting todo statistics...")
                result = await session.call_tool("get_todo_stats", arguments={})
                print(result.content[0].text)
                
                # 4. Complete a todo (we need to extract the ID from the creation result)
                print("\n4. Completing a todo...")
                # Extract the first todo ID (you'd normally parse this properly)
                todo_id = result1.content[0].text.split("ID: ")[1].strip()
                result = await session.call_tool("complete_todo", arguments={"todo_id": todo_id})
                print(f"   {result.content[0].text}")
                
                # 5. List pending todos
                print("\n5. Listing pending todos...")
                result = await session.call_tool("list_todos", arguments={"filter_by": "pending"})
                print(result.content[0].text)
                
                # 6. Update a todo
                print("\n6. Updating a todo...")
                # Get the second todo ID
                todo_id2 = result2.content[0].text.split("ID: ")[1].strip()
                result = await session.call_tool(
                    "update_todo", 
                    arguments={
                        "todo_id": todo_id2,
                        "priority": "high",
                        "description": "Create comprehensive README with examples and API documentation"
                    }
                )
                print(f"   {result.content[0].text}")
                
                # 7. Get specific todo details
                print("\n7. Getting todo details...")
                result = await session.call_tool("get_todo", arguments={"todo_id": todo_id2})
                print(result.content[0].text)
                
                # 8. Final stats
                print("\n8. Final statistics...")
                result = await session.call_tool("get_todo_stats", arguments={})
                print(result.content[0].text)
                
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR during test: {e}")
        print("\nDetailed error:")
        traceback.print_exc()
        print("\nMake sure the server is running on http://localhost:8050")

async def interactive_client():
    """Interactive client for testing individual commands"""
    
    try:
        async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                print("Connected to Todo List MCP Server!")
                print("Type 'help' for available commands or 'quit' to exit")
                
                while True:
                    try:
                        command = input("\n> ").strip().lower()
                        
                        if command == "quit":
                            break
                        
                        elif command == "help":
                            print("\nAvailable commands:")
                            print("  list [all|pending|completed] - List todos")
                            print("  create <title> - Create a new todo")
                            print("  complete <id> - Mark todo as completed")
                            print("  delete <id> - Delete a todo")
                            print("  stats - Show todo statistics")
                            print("  quit - Exit")
                        
                        elif command.startswith("list"):
                            parts = command.split()
                            filter_by = parts[1] if len(parts) > 1 else "all"
                            result = await session.call_tool("list_todos", arguments={"filter_by": filter_by})
                            print(result.content[0].text)
                        
                        elif command.startswith("create "):
                            title = command[7:].strip()
                            if title:
                                result = await session.call_tool("create_todo", arguments={"title": title})
                                print(result.content[0].text)
                            else:
                                print("Please provide a title for the todo")
                        
                        elif command.startswith("complete "):
                            todo_id = command[9:].strip()
                            if todo_id:
                                result = await session.call_tool("complete_todo", arguments={"todo_id": todo_id})
                                print(result.content[0].text)
                            else:
                                print("Please provide a todo ID")
                        
                        elif command.startswith("delete "):
                            todo_id = command[7:].strip()
                            if todo_id:
                                result = await session.call_tool("delete_todo", arguments={"todo_id": todo_id})
                                print(result.content[0].text)
                            else:
                                print("Please provide a todo ID")
                        
                        elif command == "stats":
                            result = await session.call_tool("get_todo_stats", arguments={})
                            print(result.content[0].text)
                        
                        else:
                            print("Unknown command. Type 'help' for available commands.")
                    
                    except Exception as e:
                        print(f"Error: {e}")
                        
    except Exception as e:
        print(f"\n❌ ERROR: Could not connect to server: {e}")
        print("\nMake sure the server is running on http://localhost:8050")

if __name__ == "__main__":
    print("Todo List MCP Client")
    print("1. Run automated tests")
    print("2. Interactive mode")
    choice = input("Select mode (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_todo_server())
    elif choice == "2":
        asyncio.run(interactive_client())
    else:
        print("Invalid choice")