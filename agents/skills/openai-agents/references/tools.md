# Tools

## Function Tools

Two ways to create function tools:

**Decorator** (simplest):
```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny."

agent = Agent(
    name="Weather Agent",
    instructions="Help users with weather queries.",
    tools=[get_weather],
)
```

**FunctionTool class** (more control):
```python
from agents import FunctionTool
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(description="The city name")

async def get_weather_handler(input_str: str) -> dict:
    """Async handler for weather tool."""
    data = WeatherInput.model_validate_json(input_str)
    return {"weather": f"Sunny in {data.city}"}

weather_tool = FunctionTool(
    name="get_weather",
    description="Get weather for a city",
    params_json_schema=WeatherInput.model_json_schema(),
    on_invoke_tool=get_weather_handler,
)

agent = Agent(tools=[weather_tool], ...)
```

**When to use FunctionTool class vs decorator**:
- Use `@function_tool` for simple tools with basic types
- Use `FunctionTool` class when you need:
  - Async handlers
  - Complex input validation with Pydantic
  - Custom error handling
  - Tool output type control

## Built-in Tools

**WebSearchTool**: Search the web
```python
from agents import WebSearchTool

agent = Agent(
    name="Research Agent",
    instructions="Search the web and provide answers.",
    tools=[WebSearchTool()],
)
```

**FileSearchTool**: Search vector stores
```python
from agents import FileSearchTool

agent = Agent(
    name="Document Agent",
    instructions="Search through uploaded documents.",
    tools=[FileSearchTool(vector_store_ids=["vs_..."])],
)
```

**CodeInterpreterTool**: Execute Python code
```python
from agents import CodeInterpreterTool

agent = Agent(
    name="Data Analysis Agent",
    instructions="Analyze data and create visualizations.",
    tools=[CodeInterpreterTool()],
)
```

**ComputerTool**: Control a computer/browser
```python
from agents import ComputerTool, Environment

agent = Agent(
    name="Web Automation Agent",
    instructions="Automate web browser tasks.",
    tools=[ComputerTool(display_number=1)],
    environment=Environment(
        browser_v2_server_endpoint="localhost:8000",
    ),
)
```

**ImageGenerationTool**: Generate images
```python
from agents import ImageGenerationTool

agent = Agent(
    name="Creative Agent",
    instructions="Generate images based on requests.",
    tools=[ImageGenerationTool()],
)
```

## Tool Namespaces

Organize tools with `@tool_namespace`:

```python
from agents import tool_namespace, function_tool

@tool_namespace("weather")
class WeatherTools:
    @function_tool
    def get_current(city: str) -> str:
        return f"Current: sunny in {city}"

    @function_tool
    def get_forecast(city: str, days: int) -> str:
        return f"Forecast for {city}: sunny for {days} days"

agent = Agent(
    tools=[WeatherTools()],
    # Tools become: weather.get_current, weather.get_forecast
)
```

## Tool Context Access

Access context from tool handlers:

```python
from agents import FunctionTool, RunContextWrapper
from pydantic import BaseModel

class ToolInput(BaseModel):
    query: str

class AppContext:
    user_id: str
    session_data: dict

async def search_handler(
    wrapper: RunContextWrapper[AppContext],
    input_str: str,
) -> dict:
    """Tool handler with context access."""
    input_data = ToolInput.model_validate_json(input_str)

    # Access context
    user_id = wrapper.context.user_id

    return {"results": [...]}
```
