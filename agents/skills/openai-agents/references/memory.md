# Memory and Sessions

## Session Basics

Persist conversation state across requests:

```python
from agents import Agent, Session

# Define your session
class MySession(Session):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: list[dict] = []

    async def load_history(self) -> list[TResponseInputItem]:
        return self.history

    async def save_history(self, items: list[TResponseInputItem]) -> None:
        self.history = items

    async def reset_history(self) -> None:
        self.history = []

# Use session
session = MySession("session_123")
result = await Runner.run(agent, "Hello", session=session)
```

## OpenAI Conversations Session

Use OpenAI's conversation storage:

```python
from agents import Agent, OpenAIConversationsSession, Runner

agent = Agent(name="Agent", instructions="...")

session = OpenAIConversationsSession(
    conversation_id="conv_123",
    service_tier="auto",
)

result = await Runner.run(
    agent,
    "Continue our conversation",
    session=session,
)
```

## Session with Compaction

Automatically compress long conversations:

```python
from agents import OpenAIResponsesCompactionSession

session = OpenAIResponsesCompactionSession(
    conversation_id="conv_123",
    compaction_args=OpenAIResponsesCompactionArgs(
        max_content_items=100,  # Compress when this many items
        strategy="summary",  # How to compress
    ),
)

result = await Runner.run(agent, "Continue", session=session)
```
