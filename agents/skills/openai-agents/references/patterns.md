# Common Patterns

## Research → Analysis → Report

```python
from agents import Agent, handoff, Runner

research_agent = Agent(
    name="Research",
    instructions="Gather information on the topic.",
    tools=[WebSearchTool()],
)

analysis_agent = Agent(
    name="Analysis",
    instructions="Analyze the research findings.",
)

report_agent = Agent(
    name="Report",
    instructions="Create a final report.",
)

# Set up handoffs
research_to_analysis = handoff(
    agent=analysis_agent,
    description="When research is complete",
)
analysis_to_report = handoff(
    agent=report_agent,
    description="When analysis is done",
)

main_agent = Agent(
    name="Coordinator",
    instructions="Coordinate research, analysis, and report.",
    handoffs=[research_agent, analysis_agent, report_agent],
    tools=[research_to_analysis, analysis_to_report],
)
```

## Tool-First Agent

```python
from agents import Agent, function_tool

@function_tool
def get_user_data(user_id: str) -> dict:
    """Retrieve user data."""
    return {"name": "John", "email": "john@example.com"}

@function_tool
def update_user(user_id: str, updates: dict) -> str:
    """Update user data."""
    return f"Updated user {user_id}"

agent = Agent(
    name="User Manager",
    instructions="""
    When asked about users, first use get_user_data.
    When asked to update users, use update_user.
    Always call tools before answering.
    """,
    tools=[get_user_data, update_user],
)
```

## Context-Rich Agent

```python
from dataclasses import dataclass
from agents import Agent, RunContextWrapper

@dataclass
class Context:
    user_id: str
    permissions: list[str]
    app_state: dict

def contextual_instructions(
    context: RunContextWrapper[Context],
    agent: Agent,
) -> str:
    perms = context.context.permissions
    return f"""
    You have these permissions: {', '.join(perms)}.
    Deny requests that require permissions you don't have.
    """

agent = Agent(
    name="Auth Agent",
    instructions=contextual_instructions,
)

app_context = Context(
    user_id="user_123",
    permissions=["read", "write"],
    app_state={},
)
result = await Runner.run(agent, "Delete everything", context=app_context)
```
