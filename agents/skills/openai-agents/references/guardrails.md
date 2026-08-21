# Guardrails

## Input Guardrails

Validate or filter user input before processing:

```python
from agents import Agent, input_guardrail, Runner

@input_guardrail
def check_sensitive_topics(
    context: RunContextWrapper,
    agent: Agent,
    input_data: str,
) -> InputGuardrailResult:
    """Check if input contains sensitive topics."""
    sensitive = ["password", "credit card", "ssn"]
    if any(topic in input_data.lower() for topic in sensitive):
        return InputGuardrailResult(
            tripwire_triggered=True,
            output="I cannot help with sensitive personal information.",
        )
    return InputGuardrailResult(tripwire_triggered=False, output=input_data)

agent = Agent(
    name="Safe Agent",
    instructions="Be helpful and safe.",
    input_guardrails=[check_sensitive_topics],
)

result = await Runner.run(agent, "What's my password?")
# Returns: "I cannot help with sensitive personal information."
```

## Output Guardrails

Validate or filter agent output before returning:

```python
from agents import output_guardrail

@output_guardrail
def check_output_safety(
    context: RunContextWrapper,
    agent: Agent,
    output: str,
) -> OutputGuardrailResult:
    """Ensure output is safe and appropriate."""
    if len(output) > 1000:
        return OutputGuardrailResult(
            tripwire_triggered=True,
            output="Response too long. Please be more specific.",
        )
    return OutputGuardrailResult(tripwire_triggered=False, output=output)

agent = Agent(
    name="Concise Agent",
    instructions="...",
    output_guardrails=[check_output_safety],
)
```

## Tool Guardrails

Guard tool inputs and outputs:

```python
from agents import (
    Agent,
    tool_input_guardrail,
    tool_output_guardrail,
)

@tool_input_guardrail
def validate_search_query(
    context: RunContextWrapper,
    agent: Agent,
    tool: Tool,
    tool_arguments: dict,
) -> ToolInputGuardrailResult:
    """Validate tool input."""
    if len(tool_arguments.get("query", "")) < 3:
        return ToolInputGuardrailResult(
            tripwire_triggered=True,
            output="Query too short",
        )
    return ToolInputGuardrailResult(tripwire_triggered=False, output=tool_arguments)

@tool_output_guardrail
def sanitize_search_results(
    context: RunContextWrapper,
    agent: Agent,
    tool: Tool,
    tool_output: str,
) -> ToolOutputGuardrailResult:
    """Sanitize tool output."""
    # Filter or modify tool output
    return ToolOutputGuardrailResult(
        tripwire_triggered=False,
        output=tool_output,
    )

agent = Agent(
    name="Guarded Agent",
    instructions="...",
    tool_input_guardrails=[validate_search_query],
    tool_output_guardrails=[sanitize_search_results],
)
```
