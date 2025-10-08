#!/usr/bin/env python

import boto3
import http.client
import json
import logging
import os
import sys

from datetime import datetime, timedelta
from botocore.config import Config
from strands import Agent, tool
from strands.models.bedrock import BedrockModel


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

RAPID_API_KEY = os.getenv('RAPID_API_KEY', '')
if not RAPID_API_KEY:
    logger.error('RAPID_API_KEY environment variable is not set')
    sys.exit(1)


def send_request(hostname, url, method='GET'):
    conn = http.client.HTTPSConnection(hostname)
    headers = {
        'x-rapidapi-key': RAPID_API_KEY,
        'x-rapidapi-host': hostname
    }
    conn.request(method, url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode('utf-8')


@tool
def search_airbnb(ne_latitude: str, ne_longitude: str, sw_latitude: str, sw_longitude: str, checkin_date: str, checkout_date: str, currency: str = 'USD', page: str = '1', adults: str = '1', children: str = '0') -> str:
    """Search for hotels by geographic coordinates using AIRBNB
    API:
        https://rapidapi.com/ntd119/api/airbnb-search    
    Args:
        ne_latitude: Latitude of the northeastern corner of the search area.
        ne_longitude: Longitude of the northeastern corner of the search area.
        sw_latitude: Latitude of the southwestern corner of the search area.
        sw_longitude: Longitude of the southwestern corner of the search area.
        checkin_date: Check-in date in YYYY-MM-DD format.
        checkout_date: Check-out date in YYYY-MM-DD format.
        currency: Currency code for pricing (default: 'USD').
        page: Page number for paginated results (default: 1).
        adults: Number of adults (default: 1).
        children: Number of children (default: 0).
        
    Returns:
        JSON string containing hotel search results.
    Warning:
        The free tier for this API has a limit of 100 calls per month
    """
    url = f'/api/v2/searchPropertyByGEO?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&currency={currency}&totalRecords={total_records}&adults={adults}&rooms={rooms}&checkin={checkin_date}&checkout={checkout_date}&page={page_number}'
    url = f"/property/search-geo?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&currency={currency}&page={page}&checkin={checkin_date}&checkout={checkout_date}&adults={adults}&children={children}"
    response = send_request('airbnb-search.p.rapidapi.com', url)
    logger.info(response)
    return response


@tool
def search_airbnb_sg(checkin_date: str, checkout_date: str, currency: str = 'USD', page: str = '1') -> str:
    """Search for hotels by geographic coordinates using AIRBNB    
    API:
        https://rapidapi.com/ntd119/api/airbnb-search
    Args:
        checkin_date: Check-in date in YYYY-MM-DD format.
        checkout_date: Check-out date in YYYY-MM-DD format.
        currency: Currency code for pricing (default: 'USD').
        page: Page number for paginated results (default: 1).
        
    Returns:
        JSON string containing hotel search results.
    Warning:
        The free tier for this API has a limit of 100 calls per month
    """
    ne_latitude = 1.47
    ne_longitude = 104.07
    sw_latitude = 1.13
    sw_longitude = 103.59

    url = f"/property/search-geo?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&currency={currency}&page={page}&checkin={checkin_date}&checkout={checkout_date}" # &adults={adults}&children={children}"
    response = send_request('airbnb-search.p.rapidapi.com', url)
    logger.info(response)
    return response


@tool
def search_airbnb1(ne_latitude: str, ne_longitude: str, sw_latitude: str, sw_longitude: str, checkin_date: str, checkout_date: str, currency: str = 'USD', total_records: str = '10', adults: str = '1', rooms: str = '1', page_number: str = '1') -> str:
    """Search for hotels by geographic coordinates using AIRBNB
    
    Args:
        ne_latitude: Latitude of the northeastern corner of the search area.
        ne_longitude: Longitude of the northeastern corner of the search area.
        sw_latitude: Latitude of the southwestern corner of the search area.
        sw_longitude: Longitude of the southwestern corner of the search area.
        checkin_date: Check-in date in YYYY-MM-DD format.
        checkout_date: Check-out date in YYYY-MM-DD format.
        currency: Currency code for pricing (default: 'USD').
        total_records: Number of results per page (default: 20).
        adults: Number of adults (default: 1).
        rooms: Number of rooms to book (default: 1).
        page_number: Page number for paginated results (default: 1).
        
    Returns:
        JSON string containing hotel search results.

    Warning:
        The free tier for this API has a limit of 10 calls per month
    """
    url = f'/api/v2/searchPropertyByGEO?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&currency={currency}&totalRecords={total_records}&adults={adults}&rooms={rooms}&checkin={checkin_date}&checkout={checkout_date}&page={page_number}'
    response = send_request('airbnb19.p.rapidapi.com', url)
    logger.info(response)
    return response


@tool
def search_airbnb13(ne_latitude: str, ne_longitude: str, sw_latitude: str, sw_longitude: str, checkin_date: str, checkout_date: str, currency: str = 'USD', adults: str = '1', page: str = '1') -> str:
    """Search for hotels by geographic coordinates using AIRBNB
    
    Args:
        ne_latitude: Latitude of the northeastern corner of the search area.
        ne_longitude: Longitude of the northeastern corner of the search area.
        sw_latitude: Latitude of the southwestern corner of the search area.
        sw_longitude: Longitude of the southwestern corner of the search area.
        checkin_date: Check-in date in YYYY-MM-DD format.
        checkout_date: Check-out date in YYYY-MM-DD format.
        adults: Number of adults (default: 1).
        currency: Currency code for pricing (default: 'USD').
        page: Page number for paginated results (default: 1).
        
    Returns:
        JSON string containing hotel search results.
    Reference:
        https://rapidapi.com/3b-data-3b-data-default/api/airbnb13/
    Warning:
        The free tier for this API has a limit of 100 requests per month
    """
    url = f'/search-geo?ne_lat={ne_latitude}&ne_lng={ne_longitude}&sw_lat={sw_latitude}&sw_lng={sw_longitude}&checkin={checkin_date}&checkout={checkout_date}&adults={adults}&page={page}&currency={currency}'
    response = send_request('airbnb13.p.rapidapi.com', url)
    logger.info(response)
    return response


@tool
def search_airbnb45(ne_latitude: str, ne_longitude: str, sw_latitude: str, sw_longitude: str, zoomLevel: int = 10.477618217468262, typeOfPlace: str = 'entire_home') -> str:
    """Search for hotels by geographic coordinates using AIRBNB
    
    Args:
        ne_latitude: Latitude of the northeastern corner of the search area.
        ne_longitude: Longitude of the northeastern corner of the search area.
        sw_latitude: Latitude of the southwestern corner of the search area.
        sw_longitude: Longitude of the southwestern corner of the search area.
        zoomLevel: The zoom level for the searched area. Within the range of 1-20 (Default: 10.477618217468262)
        typeOfPlace: entire_home or private_place
        
    Returns:
        JSON string containing hotel search results.
    Reference:
        https://rapidapi.com/apiheya/api/airbnb45/
    Warning:
        The free tier for this API has a limit of 100 requests per month
    """
    if zoomLevel < 1 or zoomLevel > 20:
        raise ValueError("zoomLevel must be between 1 and 20")

    url = f'/api/v1/searchPropertyByCoordinates?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&zoomLevel={zoomLevel}&typeOfPlace={typeOfPlace}'
    response = send_request('airbnb45.p.rapidapi.com', url)
    logger.info(response)
    return response


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

# Airbnb search system prompt and agent
AIRBNB_SYSTEM_PROMPT = """You are a helpful travel assistant that helps users find accommodations on Airbnb.
You can search for properties using geographic coordinates.

When helping users:
1. Ask for location details if not provided
2. Ask for stay dates if not provided
3. Highlight key features of properties like amenities, ratings, and location
4. Provide price information and any special offers
5. Suggest properties that best match the user's requirements

Always be helpful and provide clear, concise property options."""

airbnb_agent = Agent(
    model=model,
    system_prompt=AIRBNB_SYSTEM_PROMPT,
    tools = [ search_airbnb_sg ]
)

PROMPT_TEMPLATE = """I'm looking for an Airbnb in {city}.
I'll be arriving on {arrival_str} and departing on {departure_str}.
I need a place with good WiFi and close to downtown.
Can you help me find some options?"""

SINGAPORE = """Singapore (NE Latitude = 1.47, NE Longitude = 104.07, SW Latitude = 1.13, SW Longitude = 103.59)"""

def airbnb_booking_demo_strands(arrival_str, departure_str, city):
    # Example prompt for Airbnb booking
    prompt = PROMPT_TEMPLATE.format(city=city, arrival_str=arrival_str, departure_str=departure_str)
    print(f"Sending prompt to agent: {prompt}")
    response = airbnb_agent(prompt)

def airbnb_booking_demo_sg(arrival_str, departure_str):
    response = search_airbnb_sg(arrival_str, departure_str)
    r = json.loads(response)
    response_str = json.dumps(r, indent=2, default=str)
    print(response_str)
    with open('airbnb.json', 'w') as f:
        f.write(response_str)
        print(f"Saved response json to airbnb.json")

def get_arrival_departure_str(days_timedelta = 2):
    # Calculate dates for one month from now
    today = datetime.now()
    arrival_date = today + timedelta(days=30)
    departure_date = arrival_date + timedelta(days=days_timedelta)

    # Format dates as YYYY-MM-DD
    arrival_str = arrival_date.strftime('%Y-%m-%d')
    departure_str = departure_date.strftime('%Y-%m-%d')
    return arrival_str, departure_str


if __name__ == '__main__':
    arrival_str, departure_str = get_arrival_departure_str(days_timedelta=7)
    print(f"Arrival: {arrival_str}, Departure: {departure_str}")
    airbnb_booking_demo_strands(arrival_str, departure_str, "Singapore")
    # airbnb_booking_demo_sg(arrival_str, departure_str)
