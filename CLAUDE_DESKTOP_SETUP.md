# Setting up Todo MCP Server with Claude Desktop

## Overview

This guide shows you how to connect your Todo MCP Server to Claude Desktop, allowing you to manage your todos directly through Claude's interface.

## Installation Methods

### Method 1: Using MCP Install (Easiest)

If you have the MCP CLI installed:

```bash
# Navigate to your project directory
cd ToDo-MCP-Server

# Install the server to Claude Desktop
mcp install server_stdio.py
```

This will automatically add your server to Claude Desktop's configuration.

### Method 2: Manual Configuration

1. **Find your Claude Desktop configuration file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Edit the configuration file** to add your server:

```json
{
  "mcpServers": {
    "todo-list": {
      "command": "python",
      "args": ["/full/path/to/your/server_stdio.py"],
      "env": {}
    }
  }
}
```

**Important:** Replace `/full/path/to/your/server_stdio.py` with the actual full path to your server file.

For example:
- macOS/Linux: `/Users/yourusername/projects/todo-mcp-server/server_stdio.py`
- Windows: `C:\\Users\\YourUsername\\projects\\todo-mcp-server\\server_stdio.py`

### Method 3: Using UV (Recommended for Python projects)

If you're using UV for Python dependency management:

```json
{
  "mcpServers": {
    "todo-list": {
      "command": "uv",
      "args": ["run", "/full/path/to/your/server_stdio.py"],
      "env": {}
    }
  }
}
```

## Verifying the Setup

1. **Restart Claude Desktop** after updating the configuration

2. **Check if the server is connected:**
   - In Claude Desktop, you should see "todo-list" in the MCP servers list
   - Try asking Claude: "What MCP tools do you have available?"

3. **Test the integration:**
   - "Create a high priority task to review the quarterly report"
   - "Show me my pending todos"
   - "Mark the first task as completed"

## Usage Examples

Once connected, you can interact with your todos naturally:

```
You: Add a task to buy groceries tomorrow
Claude: I'll create that task for you.
[Creates todo with appropriate details]

You: What do I need to do today?
Claude: Let me check your pending tasks...
[Lists all pending todos]

You: Complete the task about groceries
Claude: I'll mark that task as completed.
[Marks the specific todo as done]
```

## Troubleshooting

### Server not appearing in Claude Desktop

1. **Check the configuration file syntax** - Make sure the JSON is valid
2. **Verify the Python path** - Ensure Python is in your system PATH
3. **Use absolute paths** - Always use full paths in the configuration
4. **Check permissions** - Make sure the script is executable

### Server appears but tools don't work

1. **Check Python environment** - Make sure MCP is installed:
   ```bash
   pip install mcp
   ```

2. **Test the server manually**:
   ```bash
   python server_stdio.py
   ```
   You should see no output (it's waiting for stdio input)

3. **Check the logs**:
   - Claude Desktop logs can help identify issues
   - Look for Python errors or missing dependencies

### Data location

The stdio version stores todos in your home directory as `~/todo_mcp_data.json`. This keeps your todos separate from the SSE server version.

## Running Both Versions

You can run both the SSE server (for web/API access) and have the stdio version configured for Claude Desktop:

- **SSE Server** (`server.py`): For web clients, Docker, cloud deployment
- **Stdio Server** (`server_stdio.py`): For Claude Desktop integration

They can share the same todo data by configuring the same `TODOS_FILE` path, or keep them separate for different use cases.

## Benefits of Claude Desktop Integration

1. **Natural Language**: No need to remember specific commands
2. **Context Awareness**: Claude understands context from your conversation
3. **Smart Suggestions**: Claude can suggest task organization
4. **Always Available**: Access your todos whenever Claude Desktop is open

## Security Note

The stdio server runs locally on your machine and is only accessible through Claude Desktop. Your todo data remains private and is stored locally.