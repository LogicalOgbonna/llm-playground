# MCP Client with Ollama Integration

A Model Context Protocol (MCP) client that integrates with Ollama for local LLM inference and connects to MCP servers for enhanced functionality.

## Overview

This MCP client provides:
- **Ollama Integration**: Uses local Ollama models for LLM inference
- **MCP Server Connection**: Connects to MCP servers via stdio transport
- **Tool Calling**: Seamlessly executes tools provided by MCP servers
- **Interactive Chat**: Command-line interface for conversational interaction

## Prerequisites

### System Requirements
- **Node.js**: Version 18 or higher
- **npm** or **pnpm**: Package manager
- **TypeScript**: For development (installed as dev dependency)

### Ollama Installation and Setup

#### 1. Install Ollama

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
# or
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from [ollama.com](https://ollama.com/download)

#### 2. Start Ollama Service

```bash
# Start Ollama service (runs on http://localhost:11434 by default)
ollama serve
```

#### 3. Pull Required Model

The client is configured to use `mistral-small3.1:24b` by default. Pull it:

```bash
ollama pull mistral-small3.1:24b
```

**Alternative Models:**
You can modify the model in the client code. Popular alternatives:
```bash
# Smaller, faster models
ollama pull llama3.2:3b
ollama pull mistral:7b

# Larger, more capable models
ollama pull llama3.1:70b
ollama pull codellama:34b
```

#### 4. Verify Ollama Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test model inference
ollama run mistral-small3.1:24b "Hello, how are you?"
```

## Installation

1. Navigate to the client directory:
   ```bash
   cd mcp/stdio/client
   ```

2. Install dependencies:
   ```bash
   pnpm install
   # or
   npm install
   ```

3. Build the TypeScript code:
   ```bash
   pnpm run build
   # or
   npm run build
   ```

4. Create environment file (optional):
   ```bash
   cp .env.example .env  # if exists
   # Edit .env with any required configurations
   ```

## Usage

### Basic Usage

Run the client with a path to an MCP server:

```bash
node ./build/example/index.js <path_to_server_script>
```

**Examples:**

```bash
# Using the weather server from this project
node ./build/example/index.js ../servers/build/example/index.js

# Using a Python MCP server
node ./build/example/index.js /path/to/server.py

# Using any JavaScript MCP server
node ./build/example/index.js /path/to/server.js
```

### Interactive Chat Session

Once connected, you'll enter an interactive chat mode:

```
MCP Client Started!
Type your queries or 'quit' to exit.

Query: What's the weather like in San Francisco?
```

The client will:
1. Send your query to the Ollama model
2. If the model needs tools, it will call the appropriate MCP server tools
3. Display the enhanced response with tool results

### Example Conversation

```
Query: Get weather alerts for California

[Tool get-alerts called with: {"state":"CA"}]

Active alerts for CA:

Event: Heat Advisory
Area: San Francisco Bay Area
Severity: Minor
Status: Actual
Headline: Heat Advisory until 8 PM PDT this evening
---

Query: What's the forecast for latitude 37.7749, longitude -122.4194?

[Tool get-forecast called with: {"latitude":37.7749,"longitude":-122.4194}]

Forecast for 37.7749, -122.4194:

Tonight:
Temperature: 62°F
Wind: 5 mph W
Partly cloudy with light winds
---
```

## Configuration

### Model Configuration

To change the Ollama model, edit `example/server.ts`:

```typescript
const response = await this.llm.chat({
  model: "mistral-small3.1:24b", // Change this line
  messages,
  tools: this.tools,
});
```

### Environment Variables

Create a `.env` file in the client directory:

```bash
# Optional: Ollama API endpoint (default: http://localhost:11434)
OLLAMA_HOST=http://localhost:11434

# Optional: Debug mode
DEBUG=true
```

## Development

### Project Structure

```
mcp/stdio/client/
├── example/
│   ├── index.ts              # Main entry point
│   └── server.ts             # MCPClient class implementation
├── build/                    # Compiled JavaScript output
├── node_modules/             # Dependencies
├── package.json              # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── .env                     # Environment variables (optional)
└── README.md                # This file
```

### Key Components

#### MCPClient Class (`server.ts`)

The main client implementation:

- **Constructor**: Initializes Ollama and MCP client instances
- **connectToServer()**: Establishes connection to MCP server via stdio
- **processQuery()**: Handles user queries with tool calling support
- **chatLoop()**: Provides interactive command-line interface
- **cleanup()**: Properly closes connections

#### Main Entry Point (`index.ts`)

Simple wrapper that:
1. Validates command line arguments
2. Creates MCPClient instance
3. Connects to specified server
4. Starts interactive chat loop

### Building from Source

```bash
# Install dependencies
pnpm install

# Build TypeScript
pnpm run build

# Run the client
node ./build/example/index.js <server_path>
```

### Supported Server Types

The client supports both JavaScript and Python MCP servers:

- **JavaScript servers**: `.js` files executed with Node.js
- **Python servers**: `.py` files executed with `python3` (or `python` on Windows)

## Tool Integration

### How Tool Calling Works

1. **Query Processing**: User input is sent to Ollama model
2. **Tool Detection**: If model determines tools are needed, it generates tool calls
3. **Tool Execution**: Client calls the appropriate MCP server tools
4. **Response Integration**: Tool results are fed back to the model
5. **Final Response**: Model generates enhanced response with tool data

### Tool Call Format

Tools are automatically converted to Ollama's expected format:

```javascript
{
  name: "tool-name",
  type: "function",
  function: {
    name: "tool-name",
    description: "Tool description",
    parameters: { /* JSON Schema */ }
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Ollama Not Running
```
Error: connect ECONNREFUSED 127.0.0.1:11434
```
**Solution**: Start Ollama service with `ollama serve`

#### 2. Model Not Found
```
Error: model "mistral-small3.1:24b" not found
```
**Solution**: Pull the model with `ollama pull mistral-small3.1:24b`

#### 3. Server Connection Failed
```
Failed to connect to MCP server
```
**Solutions**:
- Verify server script path is correct
- Ensure server script is executable
- Check server has required dependencies installed

#### 4. Tool Call Errors
```
Error calling tool: [tool-name]
```
**Solutions**:
- Verify MCP server is running properly
- Check tool parameters match expected schema
- Review server logs for specific errors

### Debug Mode

Enable detailed logging:

```bash
DEBUG=* node ./build/example/index.js <server_path>
```

### Performance Tips

1. **Model Selection**: Use smaller models for faster responses:
   - `mistral:7b` - Good balance of speed and capability
   - `llama3.2:3b` - Very fast, basic capability
   
2. **Hardware Requirements**:
   - `mistral-small3.1:24b`: Requires ~16GB RAM
   - `mistral:7b`: Requires ~4GB RAM
   - `llama3.2:3b`: Requires ~2GB RAM

## Integration Examples

### With Weather Server

```bash
# Start the weather server
node ../servers/build/example/index.js

# In another terminal, start the client
node ./build/example/index.js ../servers/build/example/index.js
```

### With Custom Servers

```bash
# Any MCP-compatible server
node ./build/example/index.js /path/to/custom-server.js
```

## API Reference

### MCPClient Methods

- `connectToServer(serverScriptPath: string)`: Connect to MCP server
- `processQuery(query: string)`: Process user query with tool support  
- `chatLoop()`: Start interactive chat session
- `cleanup()`: Close connections and cleanup resources

### Dependencies

- **@modelcontextprotocol/sdk**: MCP protocol implementation
- **ollama**: Ollama client library
- **dotenv**: Environment variable management
- **readline**: Interactive CLI support

## License

ISC License

## Contributing

1. Make changes to TypeScript files in `example/`
2. Run `pnpm run build` to compile
3. Test with various MCP servers
4. Ensure Ollama integration works correctly
5. Submit pull requests with clear descriptions 