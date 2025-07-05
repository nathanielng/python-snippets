# Weather Assistant with OpenWeatherMap Tools

A project that provides weather information using Amazon Bedrock, Strands Agents, and the OpenWeatherMap API. It includes both a Chainlit web application and standalone tools for integration into your own projects.

## Prerequisites

- Python 3.9+
- OpenWeatherMap API key
- AWS credentials with access to Amazon Bedrock

## Installation

1. Create and activate a virtual environment:

```bash
uv venv && source .venv/bin/activate
```

2. Install the dependencies:

```bash
uv pip sync requirements.txt
```

## Configuration

Set the following environment variables:

```bash
# Required
export OPENWEATHERMAP_API_KEY="your_api_key"

# Optional (if not using AWS config files)
export AWS_ACCESS_KEY="your_aws_access_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
export AWS_SESSION_TOKEN="your_aws_session_token"
export AWS_DEFAULT_REGION="us-west-2"
export BEDROCK_MODEL_ID="us.amazon.nova-lite-v1:0"
```

## Project Structure

- `weather_tools.py`: Contains the tool definitions for OpenWeatherMap API endpoints
- `app.py`: Chainlit web application for interactive weather queries
- `weather_agent.py`: Example script demonstrating how to use the tools with a Strands Agent

## Available Weather Tools

### 1. get_current_weather

Fetches current weather data for a specific location.

```python
get_current_weather(lat: float, lon: float, units: str = 'metric', api_key: Optional[str] = None)
```

### 2. get_hourly_forecast

Fetches hourly weather forecast for 4 days (96 hours).

```python
get_hourly_forecast(lat: float, lon: float, units: str = 'metric', cnt: int = 96, api_key: Optional[str] = None)
```

### 3. get_forecast_3hour

Fetches 3-hour step weather forecast for 5 days (40 timestamps).

```python
get_forecast_3hour(lat: float, lon: float, units: str = 'metric', cnt: int = 40, api_key: Optional[str] = None)
```

## Running the Chainlit Web App

Start the Chainlit app:

```bash
chainlit run app.py
```

The app will be available at http://localhost:8000

## Using the Tools in Your Own Projects

1. Import the tools in your project:

```python
from weather_tools import get_current_weather, get_hourly_forecast, get_forecast_3hour
```

2. Add them to your Strands Agent:

```python
agent = Agent(
    model=your_model,
    system_prompt=your_system_prompt,
    tools=[get_current_weather, get_hourly_forecast, get_forecast_3hour]
)
```

3. The agent can now use these tools to fetch weather data when prompted by users.

## Example Script

Run the example script:

```bash
uv run weather_agent.py
```

This will create an agent that can answer questions about the weather in San Francisco.
