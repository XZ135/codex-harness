# Troubleshooting

## Agent Not Calling Tools

**Symptom**: Agent ignores available tools.

**Causes**:
1. Instructions don't suggest using tools
2. Tool description is unclear
3. Tool input schema is incorrect

**Fixes**:
1. Update instructions to encourage tool use
2. Improve tool descriptions
3. Verify tool schema

## Streaming Stops Early

**Symptom**: Stream events stop before completion.

**Causes**:
1. Client disconnects
2. Network issues
3. Agent error

**Fixes**:
1. Handle disconnections gracefully
2. Add error handling
3. Monitor stream events

## Handoff Not Working

**Symptom**: Agent doesn't handoff to another agent.

**Causes**:
1. Handoff tool not in tools list
2. Handoff description unclear
3. Context doesn't support handoff

**Fixes**:
1. Add handoff tool to tools
2. Improve handoff description
3. Check context passing

## Memory Not Persisting

**Symptom**: Agent doesn't remember previous turns.

**Causes**:
1. Session not provided
2. Session save fails
3. Session load fails

**Fixes**:
1. Provide session to Runner.run()
2. Check session.save_history()
3. Check session.load_history()
