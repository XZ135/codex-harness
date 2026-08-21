# Context and State

## RunContextWrapper

Access runtime context throughout the agent execution:

```python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper, Runner

@dataclass
class AppContext:
    user_id: str
    session_id: str
    data_store: dict

def instructions_with_context(
    context: RunContextWrapper[AppContext],
    agent: Agent[AppContext],
) -> str:
    """Instructions that access context."""
    user_id = context.context.user_id
    return f"You are helping user {user_id}. Be helpful and concise."

agent = Agent(
    name="Context Agent",
    instructions=instructions_with_context,
)

# Run with context
app_context = AppContext(
    user_id="user_123",
    session_id="session_456",
    data_store={},
)
result = await Runner.run(agent, "Help me", context=app_context)
```

## Context in Tools

Tools receive the same RunContextWrapper as the agent:

```python
from agents import FunctionTool, RunContextWrapper

async def tool_with_context(
    wrapper: RunContextWrapper[AppContext],
    input_str: str,
) -> dict:
    """Tool that accesses context."""
    user_id = wrapper.context.user_id
    # Access session, data_store, etc.
    return {"user_id": user_id, "result": "..."}
```
