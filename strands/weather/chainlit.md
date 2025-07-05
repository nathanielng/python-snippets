# Weather Assistant

This is a weather assistant powered by Amazon Bedrock and Strands Agents. It can provide:

- Current weather conditions for any location
- Hourly forecasts for up to 4 days
- 3-hour step forecasts for up to 5 days

## Setup

Before using this app, make sure to:

1. Set your OpenWeatherMap API key as an environment variable:
   ```
   export OPENWEATHERMAP_API_KEY="your_api_key"
   ```

2. Configure your AWS credentials either through environment variables or AWS config files.

## Example Questions

- "What's the current weather in San Francisco?"
- "What's the forecast for Tokyo for the next 24 hours?"
- "Will it rain in London tomorrow?"
- "What's the temperature in New York right now?"
