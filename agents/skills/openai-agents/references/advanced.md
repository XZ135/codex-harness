# Advanced Features

## Structured Output

Use Pydantic models for structured responses:

```python
from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    summary: str = Field(description="Brief summary")
    confidence: float = Field(description="Confidence score 0-1")
    insights: list[str] = Field(description="Key insights")

agent = Agent(
    name="Analysis Agent",
    instructions="Analyze and return structured results.",
    output_type=AnalysisResult,
)

result = await Runner.run(agent, "Analyze this")
# result.final_output is an AnalysisResult instance
print(result.final_output.summary)
print(result.final_output.confidence)
```

## Stop At Tools

Control when to stop after tool calls:

```python
from agents import StopAtTools

agent = Agent(
    name="Agent",
    instructions="...",
    tool_use_behavior=StopAtTools(
        stop_at_tool_names=["final_report"],  # Stop after this tool
    ),
)
```

## Max Turns

Limit the number of turns:

```python
from agents import MaxTurnsExceeded

try:
    result = await Runner.run(
        agent,
        input="...",
        max_turns=10,  # Maximum 10 turns
    )
except MaxTurnsExceeded as e:
    print(f"Exceeded max turns: {e}")
```

## Run Configuration

Advanced run configuration:

```python
from agents import RunConfig, ToolErrorFormatter

def custom_error_formatter(args: ToolErrorFormatterArgs) -> str:
    """Custom tool error formatting."""
    return f"Tool failed: {args.error}"

result = await Runner.run(
    agent,
    input="...",
    run_config=RunConfig(
        tool_error_formatter=custom_error_formatter,
        max_turns=30,
    ),
)
```

## Error Handling

Handle run errors:

```python
from agents import RunErrorHandlers, RunErrorData

async def handle_timeout(
    input: RunErrorHandlers,
    error_data: RunErrorData,
) -> RunErrorHandlerResult:
    """Handle timeout errors."""
    return RunErrorHandlerResult(
        output="Request timed out. Please try again.",
    )

result = await Runner.run(
    agent,
    input="...",
    error_handlers=RunErrorHandlers(
        handlers={
            ToolTimeoutError: handle_timeout,
        },
    ),
)
```

## MCP (Model Context Protocol)

### MCP Tools

Use MCP server tools:

```python
from agents import Agent, HostedMCPTool

agent = Agent(
    name="MCP Agent",
    instructions="Use MCP tools as needed.",
    tools=[
        HostedMCPTool(
            server_name="filesystem",
            tool_name="read_file",
        ),
    ],
)
```

### MCP Approval

Control MCP tool approvals:

```python
from agents import MCPToolApprovalFunction

async def approve_mcp_tool(
    request: MCPToolApprovalRequest,
) -> MCPToolApprovalFunctionResult:
    """Approve MCP tool calls."""
    # Custom approval logic
    if request.tool_name in ["safe_tool_1", "safe_tool_2"]:
        return MCPToolApprovalFunctionResult(approved=True)
    return MCPToolApprovalFunctionResult(approved=False)

agent = Agent(
    name="MCP Agent",
    instructions="...",
    tools=[HostedMCPTool(...)],
    mcp_tool_approval_function=approve_mcp_tool,
)
```
