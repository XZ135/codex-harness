---
name: openai-agents
description: Expert guidance for building, deploying, and optimizing AI agents using the OpenAI Agents Python SDK. Use this skill whenever working with agents, tools, streaming, handoffs, or any openai-agents functionality. This includes creating agents, implementing tools, handling streaming responses, multi-agent coordination, context management, guardrails, memory, or advanced features like reasoning content, MCP tools, or real-time capabilities.
---

# OpenAI Agents Python SDK

This skill provides comprehensive guidance for building production-ready AI agents with the OpenAI Agents Python SDK (openai-agents).

## Quick Start

The core components are:

```python
from agents import Agent, Runner

agent = Agent(
    name="My Agent",
    instructions="You are a helpful assistant.",
)

result = await Runner.run(agent, "Hello!")
```

## Key Concepts

| Concept | Description | Reference |
|---------|-------------|-----------|
| **Agent** | The core building block with name, instructions, tools, and model settings | `references/core-concepts.md` |
| **Runner** | Executes agents - use `run()` for blocking, `run_streamed()` for real-time updates | `references/core-concepts.md` |
| **Tools** | Functions agents can call - use `@function_tool` decorator or `FunctionTool` class | `references/tools.md` |
| **Context** | Runtime state passed via `RunContextWrapper` to instructions and tools | `references/context.md` |
| **Handoffs** | Transfer control between specialized agents | `references/multi-agent.md` |
| **Guardrails** | Validate/filter inputs, outputs, and tool calls | `references/guardrails.md` |
| **Sessions** | Persist conversation history across requests | `references/memory.md` |

## When to Read Each Reference

**Start here:**
- `references/core-concepts.md` - Agent lifecycle, dynamic instructions, streaming events

**When you need tools:**
- `references/tools.md` - Function tools (decorator vs class), built-in tools (WebSearch, FileSearch, CodeInterpreter, ComputerTool), tool namespaces

**For multi-agent systems:**
- `references/multi-agent.md` - Handoffs, history management, input filtering

**For runtime state:**
- `references/context.md` - RunContextWrapper, context in tools

**For model configuration:**
- `references/model-config.md` - ModelSettings (reasoning, verbosity), custom providers, retry policies

**For observability:**
- `references/hooks.md` - AgentHooks (individual agent), RunHooks (entire run lifecycle)

**For safety:**
- `references/guardrails.md` - Input/output/tool guardrails

**For persistence:**
- `references/memory.md` - Custom sessions, OpenAI Conversations Session, compaction

**For advanced features:**
- `references/advanced.md` - Structured output, StopAtTools, max turns, error handling, MCP

**For patterns:**
- `references/patterns.md` - Research → Analysis → Report, Tool-First Agent, Context-Rich Agent

**When debugging:**
- `references/troubleshooting.md` - Common issues and solutions

## Best Practices Summary

**Performance:**
- Use streaming for long-running operations
- Limit `max_turns` to prevent infinite loops
- Use appropriate model settings
- Implement retry policies for transient failures

**Reliability:**
- Add input/output guardrails at boundaries
- Use structured output when you need specific formats
- Implement proper error handlers
- Use hooks for observability and logging

**Security:**
- Validate all inputs with guardrails
- Sanitize tool outputs
- Whitelist approved tools
- Add rate limiting
- Audit tool usage

## Reference Files

For more details on the actual SDK implementation:
- Source code: `/home/zenghao/github/openai-agents-python-main-2/src/agents/`
- Examples: `/home/zenghao/github/openai-agents-python-main-2/examples/`
- Real usage: `/home/zenghao/repo/nova_graph/core/agent/`
