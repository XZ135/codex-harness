# Core Concepts

## Agent Lifecycle

An **Agent** is the core building block. It has:
- **name**: Human-readable identifier
- **instructions**: How the agent should behave (can be static string or dynamic function)
- **tools**: Available functions the agent can call
- **model_settings**: Configuration for the underlying model
- **output_type**: Optional Pydantic model for structured output

```python
from agents import Agent, Runner

agent = Agent(
    name="My Agent",
    instructions="You are a helpful assistant.",
)

result = await Runner.run(agent, "Hello!")
```

## Dynamic Instructions

Instructions can be a function that takes `RunContextWrapper[ContextType]` and `Agent[ContextType]` and returns a string. This is useful for:
- Context-aware prompts
- Personalized behavior based on runtime state
- Skill selection or routing logic

```python
from agents import Agent, RunContextWrapper, Runner

class Context:
    style: str

def dynamic_instructions(
    run_context: RunContextWrapper[Context],
    agent: Agent[Context],
) -> str:
    if run_context.context.style == "professional":
        return "Respond professionally and formally."
    else:
        return "Respond casually and friendly."

agent = Agent(
    name="Chat Agent",
    instructions=dynamic_instructions,
)
```

## The Runner

**Runner** executes agents. Two main methods:

**Non-streaming** (`Runner.run()`):
- Returns `RunResult` with `final_output`, `input_items`, `to_input_list()`
- Best for simple, blocking operations
- Easier to debug

**Streaming** (`Runner.run_streamed()`):
- Returns `RunResultStreaming` with async iterable `stream_events()`
- Provides real-time updates as the agent processes
- Essential for UX and progress feedback

```python
# Non-streaming
result = await Runner.run(agent, "What's the weather?")
print(result.final_output)

# Streaming
streamed_result = Runner.run_streamed(agent, "Tell me a joke")
async for event in streamed_result.stream_events():
    if event.type == "run_item_stream_event":
        if event.item.type == "message_output_item":
            from agents import ItemHelpers
            print(ItemHelpers.text_message_output(event.item))
```

## Stream Events

When streaming, you receive different event types:

- **`raw_response_event`**: Raw streaming deltas (usually ignore for high-level logic)
- **`agent_updated_stream_event`**: Agent changed (handoff, new agent)
- **`run_item_stream_event`**: Agent did something:
  - `tool_call_item`: Agent called a tool
  - `tool_call_output_item`: Tool returned result
  - `message_output_item`: Agent sent a message
