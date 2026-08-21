# Model Configuration

## ModelSettings

Configure model behavior:

```python
from agents import Agent, ModelSettings
from openai.types.shared import Reasoning

agent = Agent(
    name="Advanced Agent",
    instructions="Provide detailed analysis.",
    model_settings=ModelSettings(
        # Reasoning configuration (for models that support it)
        reasoning=Reasoning(
            effort="medium",  # "low", "medium", "high"
            summary="concise",  # "concise", "detailed"
        ),
        # Verbosity control
        verbosity="medium",  # "low", "medium", "high"
        # Include specific response fields
        response_include=["reasoning.encrypted_content"],
        # Max tokens
        max_tokens=48000,
        # Temperature (for compatible models)
        temperature=0.7,
    ),
)
```

## Model Providers

Use different model providers:

```python
from agents import (
    Agent,
    OpenAIProvider,
    OpenAIChatCompletionsModel,
    OpenAIResponsesModel,
    MultiProvider,
)

# OpenAI provider with custom client
from openai import AsyncOpenAI

openai_client = AsyncOpenAI(api_key="...")
provider = OpenAIProvider(
    openai_client=openai_client,
)

# Use specific model
agent = Agent(
    name="Custom Model Agent",
    instructions="...",
    model=OpenAIChatCompletionsModel(
        model="gpt-5.4",
        provider=provider,
    ),
)

# Or use MultiProvider for failover
multi_provider = MultiProvider(
    providers=[
        OpenAIProvider(openai_client=AsyncOpenAI(api_key="primary")),
        OpenAIProvider(openai_client=AsyncOpenAI(api_key="backup")),
    ],
)
```

## Retry Configuration

Handle model failures with retry policies:

```python
from agents import Agent, ModelRetrySettings, retry_policies, Runner

agent = Agent(
    name="Resilient Agent",
    instructions="...",
)

result = await Runner.run(
    agent,
    "Analyze this data",
    retry_settings=ModelRetrySettings(
        max_retries=3,
        policies=[
            retry_policies.RetryOnRateLimit(),
            retry_policies.RetryOnTimeout(),
        ],
        backoff_settings=ModelRetryBackoffSettings(
            initial_delay=1.0,
            max_delay=10.0,
            multiplier=2.0,
        ),
    ),
)
```
