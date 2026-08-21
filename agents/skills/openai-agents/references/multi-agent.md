# Multi-Agent Patterns

## Handoffs

Handoffs allow agents to transfer control to other agents based on conversation context.

```python
from agents import Agent, handoff, Runner

# Define specialized agents
research_agent = Agent(
    name="Research Agent",
    instructions="Conduct research and gather information.",
)

analysis_agent = Agent(
    name="Analysis Agent",
    instructions="Analyze data and provide insights.",
)

# Create handoff
research_to_analysis = handoff(
    agent=analysis_agent,
    description="Transfer to analysis when research is complete.",
)

# Main agent with handoffs
main_agent = Agent(
    name="Coordinator",
    instructions="Coordinate research and analysis tasks.",
    handoffs=[research_agent, analysis_agent],
    tools=[research_to_analysis],
)

# Run and observe handoffs
result = await Runner.run(main_agent, "Research and analyze X")
```

**Handoff patterns**:
- **Sequential handoffs**: Agent A → Agent B → Agent C
- **Branching handoffs**: Agent A → Agent B or C based on context
- **Hierarchical handoffs**: Coordinator → Specialist → Sub-specialist

## Handoff History Management

Control what conversation history is passed between agents:

```python
from agents import (
    get_conversation_history_wrappers,
    set_conversation_history_wrappers,
    HandoffInputFilter,
)

# Get current history mapper
mappers = get_conversation_history_wrappers()

# Set custom mapper
def custom_filter(previous_items, handoff_input_filter):
    """Custom logic to filter history."""
    # Only keep items that are relevant to the handoff
    return [item for item in previous_items if should_keep(item)]

set_conversation_history_wrappers(custom_filter)
```

## Handoff Input Filtering

Filter what input is passed when handing off:

```python
from agents import HandoffInputFilter

def filter_input(
    input_filter: HandoffInputFilter,
    handoff_input_data: HandoffInputData,
):
    """Filter the input before handoff."""
    # Modify or filter the input data
    return handoff_input_data

handoff_with_filter = handoff(
    agent=next_agent,
    input_filter=filter_input,
    description="Hand off with filtered input",
)
```
