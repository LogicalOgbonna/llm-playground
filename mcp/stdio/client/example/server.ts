import ollama, { Ollama, Tool, Message } from "ollama";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import dotenv from "dotenv";
import readline from "readline/promises";

dotenv.config();

export class MCPClient {
  private mcp: Client;
  private llm: Ollama;
  private transport: StdioClientTransport | null = null;
  private tools: Tool[] = [];

  constructor() {
    this.llm = ollama;
    this.mcp = new Client({ name: "mcp-client-cli", version: "1.0.0" });
  }

  async connectToServer(serverScriptPath: string) {
    try {
      const isJs = serverScriptPath.endsWith(".js");
      const isPy = serverScriptPath.endsWith(".py");
      if (!isJs && !isPy) {
        throw new Error("Server script must be a .js or .py file");
      }
      const command = isPy
        ? process.platform === "win32"
          ? "python"
          : "python3"
        : process.execPath;

      this.transport = new StdioClientTransport({
        command,
        args: [serverScriptPath],
      });
      this.mcp.connect(this.transport);

      const toolsResult = await this.mcp.listTools();
      this.tools = toolsResult.tools.map((tool) => {
        return {
          name: tool.name,
          type: "function",
          function: {
            name: tool.name,
            description: tool.description,
            parameters: tool.inputSchema as any,
          },
        };
      });
      console.log(
        "Connected to server with tools:",
        this.tools.map(({ function: { name } }) => name)
      );
    } catch (e) {
      console.log("Failed to connect to MCP server: ", e);
      throw e;
    }
  }

  async processQuery(query: string) {
    const messages: Message[] = [
      {
        role: "user",
        content: query,
      },
    ];

    const response = await this.llm.chat({
      model: "mistral-small3.1:24b",
      messages,
      tools: this.tools,
    });

    const finalText: string[] = [];
    
    // Add the initial response content
    if (response.message.content) {
      finalText.push(response.message.content);
    }

    // Handle tool calls if present
    if (response.message.tool_calls && response.message.tool_calls.length > 0) {
      // Add the assistant message with tool calls to conversation
      messages.push(response.message);

      for (const toolCall of response.message.tool_calls) {
        const toolName = toolCall.function.name;
        const toolArgs = toolCall.function.arguments;

        console.log(`Calling tool: ${toolName} with args:`, toolArgs);
        
        try {
          const result = await this.mcp.callTool({
            name: toolName,
            arguments: toolArgs,
          });

          finalText.push(`\n[Tool ${toolName} called with: ${JSON.stringify(toolArgs)}]`);
          
          // Add tool result as a user message (Ollama doesn't have a separate tool role)
          messages.push({
            role: "user",
            content: `Tool result: ${JSON.stringify(result.content)}`,
          });

        } catch (error) {
          console.error(`Error calling tool ${toolName}:`, error);
          finalText.push(`\n[Error calling tool ${toolName}: ${error}]`);
          
          messages.push({
            role: "user",
            content: `Tool error: ${error}`,
          });
        }
      }

      // Get final response after tool calls
      const finalResponse = await this.llm.chat({
        model: "mistral-small3.1:24b",
        messages,
      });

      if (finalResponse.message.content) {
        finalText.push("\n" + finalResponse.message.content);
      }
    }

    return finalText.join("\n");
  }

  async chatLoop() {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    try {
      console.log("\nMCP Client Started!");
      console.log("Type your queries or 'quit' to exit.");

      while (true) {
        const message = await rl.question("\nQuery: ");
        if (message.toLowerCase() === "quit") {
          break;
        }
        const response = await this.processQuery(message);
        console.log("\n" + response);
      }
    } finally {
      rl.close();
    }
  }

  async cleanup() {
    await this.mcp.close();
  }
}
