#!/usr/bin/env python

import http.client
import json
import os
import boto3
from datetime import datetime, timedelta
from botocore.config import Config

from strands import Agent, tool
from strands.models.bedrock import BedrockModel

# RapidAPI configuration
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
RAPID_API_HOSTNAME = "booking-com15.p.rapidapi.com"

conn = http.client.HTTPSConnection(RAPID_API_HOSTNAME)
headers = {
    'x-rapidapi-key': RAPID_API_KEY,
    'x-rapidapi-host': RAPID_API_HOSTNAME
}

@tool
def search_hotels(latitude: str, longitude: str, arrival_date: str, departure_date: str, radius: str = "10", adults: str = "1", children_age: str = "0%2C17", room_qty: str = "1", units: str = "metric", page_number: str = "1", temperature_unit: str = "c", languagecode: str = "en-us", currency_code: str = "USD", location: str = "US"):
    """Search for hotels by geographic coordinates using the Booking.com API.
    
    Args:
        latitude: The latitude coordinate of the search location.
        longitude: The longitude coordinate of the search location.
        arrival_date: Check-in date in YYYY-MM-DD format.
        departure_date: Check-out date in YYYY-MM-DD format.
        radius: Search radius in kilometers (small numbers like 5 tend to give errors).
        adults: Number of adults per room.
        children_age: Ages of children, comma-separated and URL-encoded (e.g., "0%2C17").
        room_qty: Number of rooms to book.
        units: Unit system for measurements ("metric" or "imperial").
        page_number: Page number for paginated results.
        temperature_unit: Temperature unit ("c" for Celsius, "f" for Fahrenheit).
        languagecode: Language code for results (e.g., "en-us").
        currency_code: Currency code for pricing (e.g., "USD").
        location: Country code for location context.
        
    Returns:
        JSON string containing hotel search results.
    """
    conn.request("GET", f"/api/v1/hotels/searchHotelsByCoordinates?latitude={latitude}&longitude={longitude}&arrival_date={arrival_date}&departure_date={departure_date}&radius={radius}&adults={adults}&children_age={children_age}&room_qty={room_qty}&units={units}&page_number={page_number}&temperature_unit={temperature_unit}&languagecode={languagecode}&currency_code={currency_code}&location={location}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

# AWS Bedrock configuration
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-lite-v1:0')

# Create AWS session
session = boto3.Session()

# Create Bedrock model
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

# Create Strands agent
SYSTEM_PROMPT = """You are a helpful travel assistant that helps users find hotels.
You can search for hotels using geographic coordinates.
Always provide helpful recommendations based on the search results."""

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[search_hotels]
)

if __name__ == '__main__':
    # Calculate dates for one month from now
    today = datetime.now()
    arrival_date = today + timedelta(days=30)
    departure_date = arrival_date + timedelta(days=2)
    
    # Format dates as YYYY-MM-DD
    arrival_str = arrival_date.strftime('%Y-%m-%d')
    departure_str = departure_date.strftime('%Y-%m-%d')
    
    # Example prompt for hotel booking
    prompt = f"""I need to book a hotel in New York City for a business trip. 
I'll be arriving on {arrival_str} and departing on {departure_str}. 
I need a hotel near Manhattan, preferably with good business facilities and WiFi.
Can you help me find some options?"""
    
    print(f"Sending prompt to agent: {prompt}")
    response = agent(prompt)
    print("\nAgent response:")
    print(response)
