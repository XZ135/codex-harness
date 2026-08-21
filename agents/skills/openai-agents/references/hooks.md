# Hooks and Lifecycle

## Agent Hooks

Monitor individual agent lifecycle:

```python
from agents import Agent, AgentHooks, AgentHookContext

class LoggingHooks(AgentHooks):
    async def on_start(
        self,
        context: AgentHookContext,
        agent: Agent,
    ) -> None:
        print(f"{agent.name} starting with: {context.turn_input}")

    async def on_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        output: Any,
    ) -> None:
        print(f"{agent.name} finished: {output}")

agent = Agent(
    name="Agent",
    instructions="...",
    hooks=LoggingHooks(),
)
```

## Run Hooks

Monitor entire run lifecycle (includes handoffs, all tools):

```python
from agents import RunHooks, ToolContext
from agents.items import ModelResponse, TResponseInputItem

class DetailedHooks(RunHooks):
    async def on_agent_start(
        self,
        context: AgentHookContext,
        agent: Agent,
    ) -> None:
        print(f"Agent {agent.name} started")

    async def on_llm_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        system_prompt: str | None,
        input_items: list[TResponseInputItem],
    ) -> None:
        print("LLM call starting")

    async def on_llm_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        response: ModelResponse,
    ) -> None:
        print("LLM call finished")

    async def on_tool_start(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
    ) -> None:
        tool_context = context  # Actually ToolContext
        print(f"Tool {tool.name} starting")

    async def on_tool_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        tool: Tool,
        result: str,
    ) -> None:
        print(f"Tool {tool.name} finished")

    async def on_handoff(
        self,
        context: RunContextWrapper,
        from_agent: Agent,
        to_agent: Agent,
    ) -> None:
        print(f"Handoff: {from_agent.name} → {to_agent.name}")

result = await Runner.run(agent, input="...", hooks=DetailedHooks())
```
