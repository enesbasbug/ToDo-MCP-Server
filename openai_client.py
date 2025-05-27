# openai_client.py
import asyncio
import json
import os
from typing import Dict, List, Any
from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TodoMCPClient:
    def __init__(self, mcp_url: str = "http://localhost:8050/sse"):
        self.mcp_url = mcp_url
        self.openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def get_available_tools(self, session) -> List[Dict[str, Any]]:
        """Get all available MCP tools"""
        tools_result = await session.list_tools()
        
        # Convert MCP tools to OpenAI function format
        openai_tools = []
        for tool in tools_result.tools:
            # Parse the description to extract parameter info
            # This is a simplified version - in production, you'd want more robust parsing
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            openai_tools.append(openai_tool)
        
        return openai_tools
    
    async def execute_tool(self, session, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute an MCP tool and return the result"""
        result = await session.call_tool(tool_name, arguments=arguments)
        return result.content[0].text
    
    async def process_user_query(self, session, user_query: str) -> str:
        """Process a user query using OpenAI and MCP tools"""
        # Get available tools
        tools = await self.get_available_tools(session)
        
        # Create the conversation
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful assistant that manages a todo list. Use the available tools to help users manage their tasks. 

Important guidelines:
1. When creating todos, ALWAYS mention the ID that was returned
2. When users want to complete/update/delete a task by number (like "2nd task"), first list the todos to see the IDs, then use the specific ID
3. To complete a todo, you need the exact todo_id (like 'todo_20250526_171415_0')
4. Be helpful and suggest using the list_todos tool if users reference tasks by position

Always be specific about what actions you're taking and include relevant IDs in your responses.

Here are the tools you could use (if necessary): {tools}"""
            },
            {
                "role": "user",
                "content": user_query
            }
        ]
        
        # Get OpenAI's response with function calling
        response = await self.openai.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        # Check if OpenAI wants to use a tool
        response_message = response.choices[0].message
        
        if response_message.tool_calls:
            # Execute the tool calls
            tool_results = []
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Executing tool: {function_name} with args: {function_args}")
                
                # Execute the MCP tool
                result = await self.execute_tool(session, function_name, function_args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "output": result
                })
            
            # Add the assistant's message with tool calls
            messages.append(response_message)
            
            # Add tool results to messages
            for tool_result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": tool_result["output"],
                    "tool_call_id": tool_result["tool_call_id"]
                })
            
            # Get final response from OpenAI
            final_response = await self.openai.chat.completions.create(
                model="gpt-4.1",
                messages=messages
            )
            
            return final_response.choices[0].message.content
        else:
            # No tool calls needed
            return response_message.content

async def main():
    print("Connecting to Todo MCP Server...")
    
    # Create client
    client = TodoMCPClient()
    
    # Use proper async context managers
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected!\n")
            
            # Example queries
            queries = [
                # "Create a high priority task to prepare for the team meeting tomorrow",
                # "What tasks do I have pending?",
                # "Show me my todo statistics",
                "Create a low priority reminder to water the plants"
            ]
            
            for query in queries:
                print(f"User: {query}")
                response = await client.process_user_query(session, query)
                print(f"Assistant: {response}\n")
                print("-" * 50 + "\n")
                
                # Small delay between queries
                await asyncio.sleep(1)
            
            # Interactive mode
            print("\nEntering interactive mode. Type 'quit' to exit.\n")
            
            while True:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                
                try:
                    response = await client.process_user_query(session, user_input)
                    print(f"Assistant: {response}\n")
                except Exception as e:
                    print(f"Error: {e}\n")

if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in a .env file")
        print("Create a .env file with: OPENAI_API_KEY=your-api-key-here")
        exit(1)
    
    asyncio.run(main())