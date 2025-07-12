#!/usr/bin/env python

import boto3
import http.client
import json
import logging
import os

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

# # Add a file handler to save logs (optional)
# file_handler = logging.FileHandler('travel_api.log')
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
# logger.addHandler(file_handler)

RAPID_API_KEY = os.getenv('RAPID_API_KEY')

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
def search_flights(from_id: str, to_id: str, departure_date: str, return_date: str, stops: str = 'none', page_no: str = '1', adults: str = '1', children: str = '0%2C17', sort: str = 'BEST', cabin_class: str = 'ECONOMY', currency: str = 'USD') -> str:
    """Search for flights based on departure and destination airports using the Booking.com API.

    Args:
        from_id (str): Departure Airport code (e.g. FRA, SIN)
        to_id (str): Destination Airport code (e.g. LAX, LON)
        departure_date (str): Departure date in YYYY-MM-DD format
        return_date (str): Return date in YYYY-MM-DD format
        stops (str, optional): Number of stops ('none' for no preference, or '0', '1', '2'). Defaults to 'none'.
        page_no (str, optional): Page number for paginated results. Defaults to '1'.
        adults (str, optional): Number of adult passengers. Defaults to '1'.
        children (str, optional): Ages of children, comma-separated and URL-encoded (e.g. "0%2C17"). Defaults to '0%2C17'.
        sort (str, optional): Sort order for results ('BEST', 'CHEAPEST', 'FASTEST'). Defaults to 'BEST'.
        cabin_class (str, optional): Cabin class ('ECONOMY', 'BUSINESS', 'FIRST'). Defaults to 'ECONOMY'.
        currency (str, optional): Currency code for pricing (e.g. 'USD'). Defaults to 'USD'.

    Returns:
        str: JSON string containing flight search results including available flights, prices, and itineraries

    Raises:
        HTTPError: If the API request fails
    """
    url = f'/api/v1/flights/searchFlights?fromId={from_id}.AIRPORT&toId={to_id}.AIRPORT&departDate={departure_date}&returnDate={return_date}&stops={stops}&pageNo={page_no}&adults={adults}&children={children}&sort={sort}&cabinClass={cabin_class}&currency_code={currency}'
    response = send_request('booking-com15.p.rapidapi.com', url)
    logger.info(response)
    return response



@tool
def search_hotels(latitude: str, longitude: str, arrival_date: str, departure_date: str, radius: str = "10", adults: str = "1", children_age: str = "0%2C17", room_qty: str = "1", units: str = "metric", page_number: str = "1", temperature_unit: str = "c", languagecode: str = "en-us", currency_code: str = "USD", location: str = "US") -> str:
    """Search for hotels by geographic coordinates using the Booking.com API.
    
    Args:
        latitude: The latitude coordinate of the search location.
        longitude: The longitude coordinate of the search location.
        arrival_date: Check-in date in YYYY-MM-DD format.
        departure_date: Check-out date in YYYY-MM-DD format.
        radius: Search radius in kilometers (minimum value is 10).
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
    url = f'/api/v1/hotels/searchHotelsByCoordinates?latitude={latitude}&longitude={longitude}&arrival_date={arrival_date}&departure_date={departure_date}&radius={radius}&adults={adults}&children_age={children_age}&room_qty={room_qty}&units={units}&page_number={page_number}&temperature_unit={temperature_unit}&languagecode={languagecode}&currency_code={currency_code}&location={location}'
    response = send_request('booking-com15.p.rapidapi.com', url)
    logger.info(response)
    return response



@tool
def search_hotel18(ne_latitude: str, ne_longitude: str, sw_latitude: str, sw_longitude: str, checkin_date: str, checkout_date: str, results_per_page: str = '20', page_number: str = '1', rooms: str = '1', adults: str = '1', languagecode: str = 'en-us', currency_code: str = 'HOTEL') -> str:
    """Search for hotels by north-east latitude and longitude,
    southwest latitude and longitude, check-in & check-out dates
    using the Booking.com API.
    
    Args:
        ne_latitude: Latitude of the northeastern corner of the search area.
        ne_longitude: Longitude of the northeastern corner of the search area.
        sw_latitude: Latitude of the southwestern corner of the search area.
        sw_longitude: Longitude of the southwestern corner of the search area.
        checkin_date: Check-in date in YYYY-MM-DD format.
        checkout_date: Check-out date in YYYY-MM-DD format.
        results_per_page: Number of results per page.
        page_number: Page number for paginated results.
        rooms: Number of rooms to book.
        adults: Number of adults per room.
        languagecode: Language code for results (e.g. 'en-us').
        currency_code: Currency code for pricing (e.g. 'USD' or 'HOTEL' to use the property's currency).
        
    Returns:
        JSON string containing hotel search results.
    """
    if (not ne_latitude) or (not ne_longitude) or (not sw_latitude) or (not sw_longitude) or (not checkin_date) or (not checkout_date):
        return json.dumps({'error': 'Missing required parameters. The required parameters are ne_latitude, ne_longitude, sw_latitude, sw_longitude, checkin_date, and checkout_date'})

    url = f'/stays/search-by-geo?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&checkinDate={checkin_date}&checkoutDate={checkout_date}&resultsPerPage={results_per_page}&page={page_number}&rooms={rooms}&adults={adults}&units=metric&languageCode={languagecode}&currencyCode={currency_code}'
    response = send_request('booking-com18.p.rapidapi.com', url)
    logger.info(response)
    return response



@tool
def search_airbnb(ne_latitude: str, ne_longitude: str, sw_latitude: str, sw_longitude: str, checkin_date: str, checkout_date: str, currency: str = 'USD', total_records: str = '20', adults: str = '1', rooms: str = '1', page_number: str = '1') -> str:
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
    """
    url = f'/api/v2/searchPropertyByGEO?neLat={ne_latitude}&neLng={ne_longitude}&swLat={sw_latitude}&swLng={sw_longitude}&currency={currency}&totalRecords={total_records}&adults={adults}&rooms={rooms}&checkin={checkin_date}&checkout={checkout_date}&page={page_number}'
    response = send_request('airbnb19.p.rapidapi.com', url)
    logger.info(response)
    return response



@tool
def search_tripadvisor_hotels(latitude: str, longitude: str, arrival_date: str, departure_date: str, adults: str = "1", children_age: str = "0%2C17", room_qty: str = "1", units: str = "metric", page_number: str = "1", temperature_unit: str = "c", languagecode: str = "en-us", currency_code: str = "USD", location: str = "US") -> str:
    """Search for hotels by geographic coordinates using the Tripadvisor API.
    
    Args:
        latitude: The latitude coordinate of the search location.
        longitude: The longitude coordinate of the search location.
        arrival_date: Check-in date in YYYY-MM-DD format.
        departure_date: Check-out date in YYYY-MM-DD format.
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
    url = f'/api/v1/hotels/searchHotelsByLocation?latitude={latitude}&longitude={longitude}&checkIn={arrival_date}&checkOut={departure_date}&pageNumber={page_number}&adults={adults}&rooms={room_qty}&currencyCode={currency_code}'
    response = send_request('tripadvisor16.p.rapidapi.com', url)
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

HOTEL_SEARCH_SYSTEM_PROMPT = """You are a helpful travel assistant that helps users find hotels.
You can search for hotels using geographic coordinates.
Always provide helpful recommendations based on the search results."""

hotel_search_agent = Agent(
    model=model,
    system_prompt=HOTEL_SEARCH_SYSTEM_PROMPT,
    tools = [ search_hotel18 ]  # [search_hotels]
)

# Flight search system prompt and agent
FLIGHT_SEARCH_SYSTEM_PROMPT = """You are a helpful travel assistant that helps users find flights.
You can search for flights between airports using airport codes.

When helping users:
1. Ask for departure and destination airports if not provided
2. Ask for travel dates if not provided
3. Suggest flexible dates if it might help find better fares
4. Recommend direct flights when available
5. Explain the trade-offs between price and convenience
6. Highlight important details like layover duration and airlines

Always provide clear, concise flight options with relevant details."""

flight_search_agent = Agent(
    model=model,
    system_prompt=FLIGHT_SEARCH_SYSTEM_PROMPT,
    tools = [ search_flights ]
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
    tools = [ search_airbnb ]
)

# TripAdvisor search system prompt and agent
TRIPADVISOR_SYSTEM_PROMPT = """You are a helpful travel assistant that helps users find hotels via TripAdvisor.
You can search for hotels using geographic coordinates.

When helping users:
1. Ask for location details if not provided
2. Ask for stay dates if not provided
3. Highlight hotel ratings and reviews
4. Mention nearby attractions and points of interest
5. Provide price information and availability

Always be helpful and provide clear, concise hotel options with relevant details."""

tripadvisor_agent = Agent(
    model=model,
    system_prompt=TRIPADVISOR_SYSTEM_PROMPT,
    tools = [ search_tripadvisor_hotels ]
)

def hotel_booking_demo(arrival_str, departure_str):
    prompt = f"""I need to book a hotel in New York City for a business trip. 
I'll be arriving on {arrival_str} and departing on {departure_str}. 
I need a hotel near Manhattan, preferably with good business facilities and WiFi.
Can you help me find some options?"""    
    print(f"Sending prompt to agent: {prompt}")
    response = hotel_search_agent(prompt)
    print(f"Hotel search response: {response}")



def flight_booking_demo(arrival_str, departure_str):
    # Example prompt for flight booking
    prompt = f"""I need to book a flight from JFK to LAX. 
I'll be arriving on {arrival_str} and departing on {departure_str}. 
What flights are available?"""    
    print(f"Sending prompt to agent: {prompt}")
    response = flight_search_agent(prompt)
    print(f"Flight search response: {response}")


def airbnb_booking_demo(arrival_str, departure_str):
    # Example prompt for Airbnb booking
    prompt = f"""I'm looking for an Airbnb in San Francisco.
I'll be arriving on {arrival_str} and departing on {departure_str}.
I need a place with good WiFi and close to downtown.
Can you help me find some options?"""
    print(f"Sending prompt to agent: {prompt}")
    response = airbnb_agent(prompt)
    print(f"Airbnb search response: {response}")


def tripadvisor_booking_demo(arrival_str, departure_str):
    # Example prompt for TripAdvisor booking
    prompt = f"""I want to find a hotel in Chicago with good reviews.
I'll be staying from {arrival_str} to {departure_str}.
I'd like something close to the city center with breakfast included.
What can you recommend?"""
    print(f"Sending prompt to agent: {prompt}")
    response = tripadvisor_agent(prompt)
    print(f"TripAdvisor search response: {response}")



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
    import sys
    
    # Default to flights if no argument is provided
    search_type = 'flights'
    
    # Get search type from command line arguments if provided
    if len(sys.argv) > 1:
        search_type = sys.argv[1].lower()
    
    # Get dates for the search
    arrival_str, departure_str = get_arrival_departure_str(days_timedelta=7)
    
    # Call the appropriate function based on the search type
    if search_type == 'hotel':
        hotel_booking_demo(arrival_str, departure_str)
    elif search_type == 'flights':
        flight_booking_demo(arrival_str, departure_str)
    elif search_type == 'airbnb':
        airbnb_booking_demo(arrival_str, departure_str)
    elif search_type == 'tripadvisor':
        tripadvisor_booking_demo(arrival_str, departure_str)
    else:
        print(f"Invalid search type: {search_type}")
        print("Valid options are: 'hotel', 'flights', 'airbnb', 'tripadvisor'")
