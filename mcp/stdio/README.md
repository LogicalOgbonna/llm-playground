# MCP Stdio Transport Implementation

This folder contains implementations of the Model Context Protocol (MCP) using **stdio transport** - a communication method where client and server exchange JSON-RPC messages over standard input/output streams.

## Overview

The stdio transport is one of the core transport mechanisms for MCP, allowing seamless communication between MCP clients and servers through stdin/stdout. This approach is particularly useful for:

- **Process-based isolation**: Each server runs in its own process
- **Language agnostic**: Supports servers written in any language
- **Simple integration**: Easy to integrate with existing tools and workflows
- **Debugging friendly**: Messages can be easily logged and inspected

## Folder Structure

```
mcp/stdio/
├── client/                   # MCP Client implementation
│   ├── example/
│   │   ├── index.ts         # Client entry point
│   │   └── server.ts        # MCPClient class with Ollama integration
│   ├── package.json         # Client dependencies
│   └── README.md           # Client documentation
├── servers/                 # MCP Server implementation  
│   ├── example/
│   │   ├── index.ts         # Weather server implementation
│   │   └── utils/           # Server utilities
│   ├── package.json         # Server dependencies
│   └── README.md           # Server documentation
└── README.md               # This file
```

## How Stdio Transport Works

### Communication Flow

The stdio transport establishes a bidirectional communication channel where:

1. **Client** spawns the **Server** as a child process
2. **Client** sends JSON-RPC requests to Server's **stdin**
3. **Server** processes requests and sends JSON-RPC responses to **stdout**
4. **Server** can send logs/errors to **stderr** (separate from protocol messages)

### Message Format

All messages follow the JSON-RPC 2.0 specification:

```json
{
  "jsonrpc": "2.0",
  "id": "unique-request-id",
  "method": "method-name",
  "params": { /* method parameters */ }
}
```

## Pseudo Code Implementation

### Client Side (Pseudo Code)

```pseudo
class MCPStdioClient:
    process: ChildProcess
    transport: StdioTransport
    
    function connectToServer(serverScriptPath):
        // Spawn server process
        process = spawn_child_process(
            command: determine_runtime(serverScriptPath),  // node, python3, etc.
            args: [serverScriptPath],
            stdio: ['pipe', 'pipe', 'pipe']  // stdin, stdout, stderr
        )
        
        // Create transport wrapper
        transport = StdioTransport(
            stdin: process.stdin,
            stdout: process.stdout
        )
        
        // Initialize MCP connection
        send_initialize_request()
        wait_for_initialize_response()
        
        // List available tools
        tools = send_list_tools_request()
        store_tools_for_llm(tools)
    
    function processQuery(userQuery):
        // Send query to LLM with available tools
        llmResponse = llm.chat(
            messages: [{ role: 'user', content: userQuery }],
            tools: available_tools
        )
        
        // Handle tool calls if present
        if llmResponse.has_tool_calls():
            for each toolCall in llmResponse.tool_calls:
                // Call MCP server tool
                result = send_call_tool_request(
                    name: toolCall.name,
                    arguments: toolCall.arguments
                )
                
                // Feed result back to LLM
                add_tool_result_to_conversation(result)
            
            // Get final response from LLM
            finalResponse = llm.chat(updated_conversation)
            return finalResponse
        
        return llmResponse
    
    function send_request(method, params):
        request = {
            jsonrpc: "2.0",
            id: generate_unique_id(),
            method: method,
            params: params
        }
        
        // Write JSON to server's stdin
        write_to_stdin(JSON.stringify(request) + '\n')
        
        // Read response from server's stdout
        response_line = read_line_from_stdout()
        response = JSON.parse(response_line)
        
        if response.error:
            throw MCPError(response.error)
        
        return response.result
```

### Server Side (Pseudo Code)

```pseudo
class MCPStdioServer:
    tools: Map<string, ToolHandler>
    transport: StdioTransport
    
    function initialize():
        transport = StdioTransport(
            stdin: process.stdin,
            stdout: process.stdout
        )
        
        // Register available tools
        register_tool("get-alerts", handle_get_alerts)
        register_tool("get-forecast", handle_get_forecast)
        
        // Start message loop
        start_message_loop()
    
    function start_message_loop():
        while true:
            try:
                // Read JSON-RPC message from stdin
                message_line = read_line_from_stdin()
                if message_line.empty():
                    break
                    
                request = JSON.parse(message_line)
                response = process_request(request)
                
                // Send response to stdout
                write_to_stdout(JSON.stringify(response) + '\n')
                
            catch error:
                // Send error response
                error_response = {
                    jsonrpc: "2.0",
                    id: request.id,
                    error: {
                        code: -32603,
                        message: error.message
                    }
                }
                write_to_stdout(JSON.stringify(error_response) + '\n')
    
    function process_request(request):
        switch request.method:
            case "initialize":
                return handle_initialize(request.params)
            
            case "tools/list":
                return handle_list_tools()
            
            case "tools/call":
                tool_name = request.params.name
                tool_args = request.params.arguments
                
                if not tools.has(tool_name):
                    throw ToolNotFoundError(tool_name)
                
                result = tools[tool_name](tool_args)
                return { content: result }
            
            default:
                throw MethodNotFoundError(request.method)
    
    function handle_get_alerts(args):
        state = args.state
        
        // Make API request
        alerts_data = fetch_weather_alerts(state)
        
        // Format and return
        formatted_alerts = format_alerts(alerts_data)
        return [{ type: "text", text: formatted_alerts }]
```

### Transport Layer (Pseudo Code)

```pseudo
class StdioTransport:
    stdin_stream: ReadableStream
    stdout_stream: WritableStream
    message_queue: Queue
    
    function send_message(message):
        json_string = JSON.stringify(message)
        write_line(stdout_stream, json_string)
    
    function receive_message():
        line = read_line(stdin_stream)
        return JSON.parse(line)
    
    function write_line(stream, content):
        stream.write(content + '\n')
        stream.flush()
    
    function read_line(stream):
        buffer = ""
        while true:
            char = stream.read(1)
            if char == '\n':
                return buffer
            buffer += char
```

## Protocol Flow Example

Here's a complete example of how a weather query flows through the system:

```pseudo
// 1. Client starts server process
CLIENT: spawn("node", ["weather-server.js"])

// 2. Initialize connection
CLIENT -> SERVER: {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {"protocolVersion": "2024-11-05"}
}

SERVER -> CLIENT: {
    "jsonrpc": "2.0",
    "id": "1",
    "result": {"protocolVersion": "2024-11-05", "capabilities": {...}}
}

// 3. List available tools
CLIENT -> SERVER: {
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list"
}

SERVER -> CLIENT: {
    "jsonrpc": "2.0",
    "id": "2",
    "result": {
        "tools": [
            {
                "name": "get-alerts",
                "description": "Get weather alerts for a state",
                "inputSchema": {...}
            }
        ]
    }
}

// 4. User asks: "Any weather alerts in California?"
// 5. LLM decides to call get-alerts tool

CLIENT -> SERVER: {
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
        "name": "get-alerts",
        "arguments": {"state": "CA"}
    }
}

SERVER -> CLIENT: {
    "jsonrpc": "2.0",
    "id": "3",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Active alerts for CA:\n\nEvent: Heat Advisory\n..."
            }
        ]
    }
}

// 6. LLM generates final response with tool data
// 7. Response shown to user
```

## Key Advantages

### 1. Process Isolation
- Each server runs in its own process
- Crashes don't affect the client
- Memory and resource isolation

### 2. Language Flexibility
```pseudo
// Server can be written in any language:
CLIENT: spawn("node", ["server.js"])     // JavaScript
CLIENT: spawn("python3", ["server.py"]) // Python  
CLIENT: spawn("./server", [])            // Go, Rust, C++, etc.
```

### 3. Simple Debugging
```pseudo
// Easy to intercept and log messages:
function debug_transport_layer():
    original_write = stdout.write
    original_read = stdin.read
    
    stdout.write = (data) => {
        log("SENT: " + data)
        original_write(data)
    }
    
    stdin.read = () => {
        data = original_read()
        log("RECEIVED: " + data)
        return data
    }
```

### 4. Standard Integration
- Works with any process spawning mechanism
- Compatible with shell scripts and system tools
- Easy to integrate with existing workflows

## Implementation Details

### Error Handling
- Network timeouts handled gracefully
- Process crashes trigger reconnection
- Malformed JSON messages logged and skipped
- Tool execution errors returned as proper JSON-RPC errors

### Performance Considerations
- Async message handling prevents blocking
- Message queuing for high-throughput scenarios
- Connection pooling for multiple servers
- Efficient JSON parsing and serialization

### Security
- Process sandboxing via OS mechanisms
- Input validation on all messages
- Resource limits on spawned processes
- Secure handling of file paths and arguments

## Usage Examples

### Basic Client Usage
```bash
# Connect to JavaScript server
node client/build/example/index.js server/build/example/index.js

# Connect to Python server  
node client/build/example/index.js /path/to/server.py

# Connect with custom arguments
node client/build/example/index.js server.js --config config.json
```

### Integration with Other Tools
```bash
# Use in shell scripts
echo '{"query": "weather in NYC"}' | node client/build/example/index.js server.js

# Integration with CI/CD
node client/build/example/index.js server.js < test_queries.json > results.json
```

## Contributing

When adding new functionality:

1. **Client changes**: Update `client/example/server.ts`
2. **Server changes**: Update `servers/example/index.ts`
3. **Protocol changes**: Update both client and server
4. **Testing**: Test with various server implementations
5. **Documentation**: Update relevant README files

## Related Documentation

- [Client Documentation](./client/README.md) - Detailed client setup with Ollama
- [Server Documentation](./servers/README.md) - Weather server implementation
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official protocol specification 