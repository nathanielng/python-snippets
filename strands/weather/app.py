#!/usr/bin/env python

import os
import boto3
import chainlit as cl
import logging

from botocore.config import Config
from strands import Agent
from strands.models.bedrock import BedrockModel
from weather_tools import get_current_weather, get_hourly_forecast, get_forecast_3hour

logger = logging.getLogger('__name__')
logging.getLogger("strands").setLevel(logging.INFO)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Load AWS Credentials from the environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', None)
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-lite-v1:0')

# Define system prompt
SYSTEM_PROMPT = """
You are a helpful weather assistant that can provide weather information for locations around the world.
You have access to tools that can fetch current weather data and forecasts.
When providing weather information, include relevant details like temperature, conditions, and any weather alerts.
"""

# Initialize the agent
def init_agent():
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

    # Create agent with our weather tools
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_current_weather, get_hourly_forecast, get_forecast_3hour]
    )
    return agent

@cl.on_chat_start
async def on_chat_start():
    # Initialize the agent
    agent = init_agent()
    
    # Store the agent in the user session
    cl.user_session.set("agent", agent)
    
    # # Send a welcome message
    # await cl.Message(
    #     content="👋 Welcome to the Weather Assistant! I can provide current weather data and forecasts for locations around the world. Please ask me about the weather in any location."
    # ).send()

example_weather_requests = [
    'What is the weather in Paris?',
    'Tell me how to prepare for a trip to Tokyo if I will be arriving tomorrow'
]

@cl.set_starters
async def set_starters():
    """Chat starter suggestions!"""
    return [
        cl.Starter(
            label = f'{example_weather_requests[0][:80]}...',
            message = f'{example_weather_requests[0]}',
        ),
        cl.Starter(
            label = f'{example_weather_requests[1][:80]}...',
            message = f'{example_weather_requests[1]}',
        ),
    ]

@cl.on_message
async def on_message(message: cl.Message):
    # Get the agent from the user session
    agent = cl.user_session.get("agent")
    
    # Send a thinking message
    msg = cl.Message(content='') # 'Thinking...')
    await msg.send()
    
    try:
        agent_stream = agent.stream_async(message.content)        
        async for event in agent_stream:
            if 'data' in event:
                text_chunk = event["data"]
                print(text_chunk, end="", flush=True)
                await msg.stream_token(text_chunk)
            elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                tool_use_chunk = f"\n[Tool use delta for: {event['current_tool_use']['name']}]\n"
                print(tool_use_chunk)
                await msg.stream_token(tool_use_chunk)  

    except Exception as e:
        # Handle errors
        error_message = f"An error occurred: {str(e)}"
        if "OpenWeatherMap API key not found" in str(e):
            error_message += "\n\nPlease make sure to set your OpenWeatherMap API key as an environment variable: `export OPENWEATHERMAP_API_KEY='your_api_key'`"
        
        await msg.stream_token(error_message)
