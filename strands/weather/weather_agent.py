import boto3
import os
from botocore.config import Config
from strands import Agent
from strands.models.bedrock import BedrockModel
from weather_tools import get_current_weather, get_hourly_forecast, get_forecast_3hour

# Load AWS Credentials from the environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', None)
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-lite-v1:0')

# Create AWS session
if AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN:
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        region_name=AWS_DEFAULT_REGION
    )
else:
    session = boto3.Session()

# Configure Bedrock model
model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    max_tokens=2048,
    boto_client_config=Config(
        read_timeout=120,
        connect_timeout=120,
        retries=dict(max_attempts=3, mode="adaptive"),
    ),
    boto_session=session
)

# Define system prompt
SYSTEM_PROMPT = """
You are a helpful weather assistant that can provide weather information for locations around the world.
You have access to tools that can fetch current weather data and forecasts.
When providing weather information, include relevant details like temperature, conditions, and any weather alerts.
"""

# Create agent with our weather tools
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_current_weather, get_hourly_forecast, get_forecast_3hour]
)

# Example usage
if __name__ == "__main__":
    # Set your OpenWeatherMap API key as an environment variable before running
    # export OPENWEATHERMAP_API_KEY="your_api_key"
    
    # Example coordinates for San Francisco
    lat = 37.7749
    lon = -122.4194
    
    # Example prompt
    prompt = "What's the current weather in San Francisco, and what's the forecast for the next 24 hours?"
    
    # Get response from agent
    response = agent(prompt)
    print(response)
