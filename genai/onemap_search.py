#!/usr/bin/env python

"""
Singapore OneMap API client for searching buildings and locations.

A Python client library for interacting with the Singapore OneMap API. Provides tools for:
- Location and address searching
- Reverse geocoding
- Public transport routing
- Finding nearby transport options
- Static map generation

Requires authentication via OneMap API credentials. Sign up at https://www.onemap.gov.sg/
"""

import boto3
# import http.client
import json
import logging
import os
import requests
import sys

from datetime import datetime  #, timedelta
from dotenv import load_dotenv
from botocore.config import Config
from strands import Agent, tool
from strands.models.bedrock import BedrockModel

from typing import Optional, Dict, Any, List
# from urllib.parse import urlencode


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()

ONEMAP_REGISTERED_EMAIL = os.getenv("ONEMAP_REGISTERED_EMAIL")
ONEMAP_REGISTERED_PASSWORD = os.getenv("ONEMAP_REGISTERED_PASSWORD")
ONEMAP_ACCESS_TOKEN = os.getenv("ONEMAP_ACCESS_TOKEN")


def get_onemap_access_token(email: str, password: str) -> Dict[str, Any]:
    """
    Get an access token from the OneMap API using email and password credentials.

    Args:
        email: Registered OneMap email address
        password: Registered OneMap password

    Returns:
        Dictionary containing:
            - access_token: The authentication token (valid for 3 days)
            - expiry_timestamp: Unix timestamp when the token expires

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If authentication fails (invalid credentials)

    Example:
        >>> token_data = get_onemap_access_token("user@example.com", "password123")
        >>> access_token = token_data['access_token']
        >>> expiry = token_data['expiry_timestamp']

    Reference:
        https://www.onemap.gov.sg/apidocs/authentication

    Note:
        - Access tokens are valid for 3 days
        - You need to register at https://www.onemap.gov.sg/ to get credentials
    """
    auth_url = "https://www.onemap.gov.sg/api/auth/post/getToken"

    # Prepare authentication payload
    payload = {
        "email": email,
        "password": password
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make POST request to get access token
        response = requests.post(auth_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse response
        token_data = response.json()

        # Check if authentication was successful
        if 'access_token' not in token_data:
            raise ValueError(f"Authentication failed: {token_data.get('error', 'Unknown error')}")

        logger.info(f"Successfully obtained access token, expires at: {token_data.get('expiry_timestamp')}")
        return token_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting access token from OneMap API: {e}")
        raise
    except ValueError as e:
        logger.error(str(e))
        raise


@tool
def search_onemap_location(
    search_val: str,
    return_geom: bool = True,
    get_addr_details: bool = True,
    page_num: int = 1,
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for a building or location using the Singapore OneMap API.

    Args:
        search_val: Building name, road name, or postal code to search for
        return_geom: If True, include geocoordinates (latitude/longitude) in response
        get_addr_details: If True, include full address details in response
        page_num: Page number for paginated results (default: 1)
        access_token: Optional OneMap access token for authentication

    Returns:
        Dictionary containing the API response with search results

    Raises:
        requests.exceptions.RequestException: If the API request fails

    Example:
        >>> result = search_onemap_location("Marina Bay Sands")
        >>> print(result['found'])  # Number of results found
        >>> for location in result['results']:
        ...     print(f"{location['SEARCHVAL']}: {location['LATITUDE']}, {location['LONGITUDE']}")

    Reference:
        https://www.onemap.gov.sg/apidocs/search
    """
    base_url = "https://www.onemap.gov.sg/api/common/elastic/search"

    # Build query parameters
    params = {
        "searchVal": search_val,
        "returnGeom": "Y" if return_geom else "N",
        "getAddrDetails": "Y" if get_addr_details else "N",
        "pageNum": page_num
    }

    # Build headers with authorization if access token is provided
    headers = {}
    if not access_token:
        access_token = ONEMAP_ACCESS_TOKEN
    headers["Authorization"] = access_token

    try:
        # Make GET request to OneMap API
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Return JSON response
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OneMap API: {e}")
        raise


@tool
def reverse_geocode(
    latitude: float,
    longitude: float,
    buffer: Optional[str] = None,
    addressType: Optional[str] = None,
    otherFeatures: Optional[str] = None,
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reverse geocode coordinates to get address information using OneMap API.

    Converts latitude/longitude coordinates (WGS84) to a physical address in Singapore.

    Args:
        latitude: Latitude coordinate (WGS84 format)
        longitude: Longitude coordinate (WGS84 format)
        buffer: Optional. Values: 0-500 (in meters). Rounds up all buildings in a circumference from a point and search building add
        addressType: Optional. Values: HDB or All. Allows users to define property types within the buffer/radius. If HDB is selected, result
        otherFeatures: Optional. Values: Y or N. Allows uses the page to retrieve information on reservoirs, playgrounds, jetties, etc. Default is N.
        access_token: Optional OneMap access token. If not provided, will attempt to
                     get one using environment variables.

    Returns:
        Dictionary containing address information including:
            - building: Building name
            - block: Block number
            - road: Road name
            - postal: Postal code
            - x: X coordinate (SVY21)
            - y: Y coordinate (SVY21)

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If coordinates are invalid or authentication fails

    Example:
        >>> # Marina Bay Sands coordinates
        >>> result = reverse_geocode(1.2834, 103.8607)
        >>> print(result['road'])
        >>> print(result['postal'])

    Reference:
        https://www.onemap.gov.sg/apidocs/reverseGeocode

    Note:
        - Requires authentication (access token)
        - Coordinates should be in WGS84 format
        - Returns SVY21 coordinates in addition to address
    """
    if not access_token:
        access_token = ONEMAP_ACCESS_TOKEN

    base_url = "https://www.onemap.gov.sg/api/public/revgeocode"

    # Build query parameters
    params = {
        "location": f"{latitude},{longitude}",
    }
    if buffer:
        params["buffer"] = buffer
    if addressType:
        params["addressType"] = addressType
    if otherFeatures:
        params["otherFeatures"] = otherFeatures

    headers = {
        'Authorization': access_token
    }

    try:
        # Make GET request to OneMap API
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse response
        result = response.json()

        # Check for errors in response
        if 'error' in result:
            raise ValueError(f"Reverse geocoding failed: {result['error']}")

        logger.info(f"Successfully reverse geocoded ({latitude}, {longitude})")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error reverse geocoding from OneMap API: {e}")
        raise
    except ValueError as e:
        logger.error(str(e))
        raise


@tool
def get_public_transport_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    date: Optional[str] = None,
    time: Optional[str] = None,
    mode: str = "TRANSIT",
    max_walk_distance: Optional[int] = None,
    num_itineraries: int = 3,
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get public transport routing information between two points using OneMap API.

    Args:
        start_lat: Starting point latitude (WGS84)
        start_lon: Starting point longitude (WGS84)
        end_lat: Ending point latitude (WGS84)
        end_lon: Ending point longitude (WGS84)
        date: Date in format "MM-DD-YYYY" (default: today's date)
        time: Time in format "HH:MM:SS" (default: current time)
        mode: Transport mode - "TRANSIT", "BUS", or "RAIL" (default: "TRANSIT")
        max_walk_distance: Maximum walking distance in meters (optional)
        num_itineraries: Number of route options to return (default: 3)
        access_token: Optional OneMap access token. If not provided, will attempt to
                     get one using environment variables.

    Returns:
        Dictionary containing route information including:
            - plan: Route plan with itineraries
            - from: Starting location details
            - to: Ending location details
            - itineraries: List of possible routes with legs, duration, distance

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If parameters are invalid or authentication fails

    Example:
        >>> # Route from Raffles Place to Changi Airport
        >>> route = get_public_transport_route(
        ...     start_lat=1.2843, start_lon=103.8512,
        ...     end_lat=1.3644, end_lon=103.9915,
        ...     mode="TRANSIT"
        ... )
        >>> print(f"Duration: {route['plan']['itineraries'][0]['duration']} seconds")

    Reference:
        https://www.onemap.gov.sg/apidocs/routing/#publicTransport

    Note:
        - Requires authentication (access token)
        - Coordinates should be in WGS84 format
        - Mode "TRANSIT" includes both bus and rail
    """
    # Get access token if not provided
    if not access_token:
        access_token = ONEMAP_ACCESS_TOKEN

    # Set default date and time if not provided
    if date is None:
        date = datetime.now().strftime("%m-%d-%Y")
    if time is None:
        time = datetime.now().strftime("%H:%M:%S")

    base_url = "https://www.onemap.gov.sg/api/public/routingsvc/route"

    # Build query parameters
    params = {
        "start": f"{start_lat},{start_lon}",
        "end": f"{end_lat},{end_lon}",
        "routeType": "pt",
        "date": date,
        "time": time,
        "mode": mode,
        "numItineraries": str(num_itineraries)
    }

    # Add optional parameters
    if max_walk_distance is not None:
        params["maxWalkDistance"] = str(max_walk_distance)

    headers = {
        "Authorization": access_token
    }

    try:
        # Make GET request to OneMap API
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse response
        result = response.json()

        # Check for errors in response
        if 'error' in result:
            raise ValueError(f"Routing failed: {result['error']}")

        logger.info(f"Successfully retrieved public transport route from ({start_lat},{start_lon}) to ({end_lat},{end_lon})")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting route from OneMap API: {e}")
        raise
    except ValueError as e:
        logger.error(str(e))
        raise


@tool
def get_nearby_transport(
    latitude: float,
    longitude: float,
    mrt_or_bus: str,
    radius_in_meters: Optional[int] = None,
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get nearby public transport information (MRT stations and bus stops) using OneMap API.

    Args:
        latitude: Latitude coordinate (WGS84 format)
        longitude: Longitude coordinate (WGS84 format)
        mrt_or_bus: Set to 'mrt' or 'bus'
        radius_in_meters: Search radius in meters (optional, defaults to 2000. Max is 5000)
        access_token: Optional OneMap access token. If not provided, will attempt to
                     get one using environment variables.

    Returns:
        Dictionary containing nearby transport information including:
            - MRT stations with name, distance, coordinates
            - Bus stops with code, name, distance, coordinates

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If coordinates are invalid or authentication fails

    Example:
        >>> # Find transport near Marina Bay Sands
        >>> transport = get_nearby_transport(1.2834, 103.8607)
        >>> for mrt in transport.get('mrt', []):
        ...     print(f"{mrt['name']}: {mrt['distance']}m away")

    Reference:
        https://www.onemap.gov.sg/apidocs/nearbytransport

    Note:
        - Requires authentication (access token)
        - Coordinates should be in WGS84 format
        - Returns both MRT stations and bus stops within specified radius
    """
    # Get access token if not provided
    if not access_token:
        access_token = ONEMAP_ACCESS_TOKEN

    if mrt_or_bus.lower() == 'mrt':
        base_url = "https://www.onemap.gov.sg/api/public/nearbysvc/getNearestMrtStops"
    elif mrt_or_bus.lower() == 'bus':
        base_url = "https://www.onemap.gov.sg/api/public/nearbysvc/getNearestBusStops"
    else:
        base_url = "https://www.onemap.gov.sg/api/public/nearbysvc/getNearestBusStops"

    # Build query parameters
    params = {
        "latitude": latitude,
        "longitude": longitude
    }
    if radius_in_meters:
        params["radius_in_meters"] = radius_in_meters

    headers = {
        "Authorization": access_token
    }

    try:
        # Make GET request to OneMap API
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse response
        result = response.json()

        # Check for errors in response
        if 'error' in result:
            raise ValueError(f"Nearby transport query failed: {result['error']}")

        logger.info(f"Successfully retrieved nearby transport for ({latitude}, {longitude})")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting nearby transport from OneMap API: {e}")
        raise
    except ValueError as e:
        logger.error(str(e))
        raise


def save_response_as_png(response_bytes: bytes, filename: str = "response.png") -> None:
    """
    Save bytes response as a PNG file.

    Args:
        response_bytes: Bytes data to save
        filename: Name of file to save to (default: response.png)
    """
    with open(filename, 'wb') as f:
        f.write(response_bytes)


@tool
def get_static_map_lat_lon(
    latitude: str,
    longitude: str,
    map_style: str = "Default",
    zoom: int = 15,
    width: int = 512,
    height: int = 512,
    # markers: Optional[List[Dict[str, Any]]] = None,
    access_token: Optional[str] = None
) -> bytes:

    """
    Generate a static map image, given latitude & longitude, using OneMap API.

    Args:
        latitude (string): Latitude coordinates in WGS84 format.
        longitud (string): Longitude coordinates in WGS84 format.
        zoom (int): Zoom level (11-19. The zoom level of the static image. The lower the value, the more zoomed out the static image)
        width (int): Image width in pixels (128-512. The width of the static image.)
        height (int): Image height in pixels (128-512. The height of the static image.)
        map_style: Map style - Choice of available base maps: night, grey, original, default and landlot
        access_token: Optional OneMap access token. If not provided, will attempt to
                     get one using environment variables.

    Returns:
        Bytes of the PNG image

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If parameters are invalid or authentication fails

    Example:
        >>> # Generate map centered on Marina Bay Sands
        >>> img_data = get_static_map(1.2834, 103.8607, zoom=16, width=800, height=600)
        >>> with open('map.png', 'wb') as f:
        ...     f.write(img_data)

        >>> # With markers
        >>> markers = [
        ...     {'lat': 1.2834, 'lon': 103.8607, 'color': 'red'},
        ...     {'lat': 1.2900, 'lon': 103.8500, 'color': 'blue'}
        ... ]
        >>> img_data = get_static_map(1.2834, 103.8607, markers=markers)

    Reference:
        https://www.onemap.gov.sg/apidocs/staticmap

    Note:
        - Requires authentication (access token)
        - Coordinates should be in WGS84 format
        - Minimum image size is 100x100 pixels
        - Returns PNG image data as bytes
    """

    # Validation
    if not access_token:
        access_token = ONEMAP_ACCESS_TOKEN
    if width < 128 or height < 128:
        raise ValueError("Width and height must be at least 128 pixels")
    if width > 512 or height > 512:
        raise ValueError("Width and height must be at most 512 pixels")
    if not 11 <= zoom <= 19:
        raise ValueError("Zoom level must be between 11 and 19")
    
    base_url = "https://www.onemap.gov.sg/api/staticmap/getStaticImage"

    # Build query parameters
    params = {
        "layerchosen": map_style,
        "latitude": latitude,
        "longitude": longitude,
        "zoom": str(zoom),
        "width": str(width),
        "height": str(height)
    }

    # markers: Optional list of marker dictionaries with keys:
    #         - lat: Marker latitude
    #         - lon: Marker longitude
    #         - color: Marker color (e.g., 'red', 'blue')
    #         - label: Optional marker label

    # Add markers if provided
    # if markers:
    #     marker_strings = []
    #     for marker in markers:
    #         marker_lat = marker.get('lat')
    #         marker_lon = marker.get('lon')
    #         marker_color = marker.get('color', 'red')
    #         marker_label = marker.get('label', '')

    #         if marker_lat is None or marker_lon is None:
    #             continue

    #         marker_str = f"latLng:{marker_lat},{marker_lon}!colour:{marker_color}"
    #         if marker_label:
    #             marker_str += f"!label:{marker_label}"
    #         marker_strings.append(marker_str)

    #     if marker_strings:
    #         params["markers"] = "&marker=".join(marker_strings)

    headers = {
        "Authorization": access_token
    }

    try:
        # Make GET request to OneMap API
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # Check if response is an image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type.lower():
            # Try to parse as JSON to check for errors
            try:
                result = response.json()
                if 'error' in result:
                    raise ValueError(f"Static map generation failed: {result['error']}")
            except:
                pass
            raise ValueError(f"Expected image response, got: {content_type}")

        save_response_as_png(response.content)
        logger.info(f"Successfully generated static map for ({center_lat}, {center_lon}) at zoom {zoom}")
        return response.content

    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating static map from OneMap API: {e}")
        raise
    except ValueError as e:
        logger.error(str(e))
        raise


@tool
def get_static_map_postal(
    postal: str,
    map_style: str = "Default",
    zoom: int = 15,
    width: int = 512,
    height: int = 512,
    # markers: Optional[List[Dict[str, Any]]] = None,
    access_token: Optional[str] = None
) -> bytes:

    """
    Generate a static map image from a postal code, using the OneMap API.

    Args:
        postal (string): Postal code.
        zoom (int): Zoom level (11-19. The zoom level of the static image. The lower the value, the more zoomed out the static image)
        width (int): Image width in pixels (128-512. The width of the static image.)
        height (int): Image height in pixels (128-512. The height of the static image.)
        map_style: Map style - Choice of available base maps: night, grey, original, default and landlot
        access_token: Optional OneMap access token. If not provided, will attempt to
                     get one using environment variables.

    Returns:
        Bytes of the PNG image

    Raises:
        requests.exceptions.RequestException: If the API request fails
        ValueError: If parameters are invalid or authentication fails

    Example:
        >>> # Generate map centered on Marina Bay Sands
        >>> img_data = get_static_map(1.2834, 103.8607, zoom=16, width=800, height=600)
        >>> with open('map.png', 'wb') as f:
        ...     f.write(img_data)

        >>> # With markers
        >>> markers = [
        ...     {'lat': 1.2834, 'lon': 103.8607, 'color': 'red'},
        ...     {'lat': 1.2900, 'lon': 103.8500, 'color': 'blue'}
        ... ]
        >>> img_data = get_static_map(1.2834, 103.8607, markers=markers)

    Reference:
        https://www.onemap.gov.sg/apidocs/staticmap

    Note:
        - Requires authentication (access token)
        - Coordinates should be in WGS84 format
        - Minimum image size is 100x100 pixels
        - Returns PNG image data as bytes
    """

    # Validation
    if not access_token:
        access_token = ONEMAP_ACCESS_TOKEN
    if width < 128 or height < 128:
        raise ValueError("Width and height must be at least 128 pixels")
    if width > 512 or height > 512:
        raise ValueError("Width and height must be at most 512 pixels")
    if not 11 <= zoom <= 19:
        raise ValueError("Zoom level must be between 11 and 19")
    
    base_url = "https://www.onemap.gov.sg/api/staticmap/getStaticImage"

    # Build query parameters
    params = {
        "layerchosen": map_style,
        "postal": postal,
        "zoom": str(zoom),
        "width": str(width),
        "height": str(height)
    }

    headers = {
        "Authorization": access_token
    }

    try:
        # Make GET request to OneMap API
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # Check if response is an image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type.lower():
            # Try to parse as JSON to check for errors
            try:
                result = response.json()
                if 'error' in result:
                    raise ValueError(f"Static map generation failed: {result['error']}")
            except:
                pass
            raise ValueError(f"Expected image response, got: {content_type}")

        save_response_as_png(response.content)
        logger.info(f"Successfully generated static map for ({center_lat}, {center_lon}) at zoom {zoom}")
        return response.content

    except requests.exceptions.RequestException as e:
        logger.error(f"Error generating static map from OneMap API: {e}")
        raise
    except ValueError as e:
        logger.error(str(e))
        raise


@tool
def get_building_info(building_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific building using its ID.

    Args:
        building_id: The unique identifier for the building

    Returns:
        Dictionary containing building information

    Raises:
        requests.exceptions.RequestException: If the API request fails

    Example:
        >>> building = get_building_info("12345")
        >>> print(building)
    """
    base_url = f"https://api.onemap.gov.sg/building/{building_id}"

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching building info from OneMap API: {e}")
        raise


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

ONEMAP_SYSTEM_PROMPT = """You are a helpful Singapore location and travel assistant powered by OneMap API.

You have access to the following tools:
1. Searching for locations, buildings, roads, and postal codes in Singapore
2. Getting address information from coordinates (reverse geocoding) 
3. Planning public transport routes between locations
4. Finding nearby MRT stations and bus stops
5. Generating static map images from coordinates or postal codes

When users ask for information:
- Search for locations using search_onemap_location
- Convert coordinates to addresses using reverse_geocode 
- Plan routes using get_public_transport_route
- Find nearby transport using get_nearby_transport
- Generate map images using get_static_map_lat_lon or get_static_map_postal

Always provide clear, helpful responses with relevant details from the API results.
For locations, include address, postal code and coordinates when available.
For routes, specify travel time, distance and step-by-step directions.
For nearby transport, list MRT stations and bus stops with distances.
"""

onemap_agent = Agent(
    model=model,
    system_prompt=ONEMAP_SYSTEM_PROMPT,
    tools=[
        search_onemap_location,
        reverse_geocode,
        get_public_transport_route,
        get_nearby_transport,
        get_building_info
    ]
)

EXAMPLE_PROMPTS = [
    "Where is Raffles Place MRT?",
    "What is the postal code for Raffles Place MRT?",
    "What is the address for postal code 048618?",
    "What is at latitude 1.283933 and longitude 103.851463?",
    "Get the public transport route from latitude 1.283933 and longitude 103.851463 to latitude 1.2900 and longitude 103.8500",
    "Find nearby MRT stations and bus stops for latitude 1.283933 and longitude 103.851463",
    # "Generate a static map for Raffles Place MRT"
]

def run_interactive_agent():
    """
    Run the OneMap agent in interactive mode, taking user input from stdin.
    """
    print("=" * 70)
    print("OneMap Singapore Assistant")
    print("=" * 70)
    print("\nWelcome! I can help you with:")
    print("  • Search for locations, buildings, and addresses in Singapore")
    print("  • Find coordinates for any address or postal code")
    print("  • Get address information from coordinates")
    print("  • Plan public transport routes")
    print("  • Find nearby MRT stations and bus stops")
    print("\nType 'exit' or 'quit' to end the session.")
    print("=" * 70)
    for i, prompt in enumerate(EXAMPLE_PROMPTS):
        print(f"\n{i}. {prompt}")
    print("=" * 70)
    print()

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nThank you for using OneMap Assistant. Goodbye!")
                break

            # Skip empty input
            if not user_input:
                continue

            # Send message to agent
            print("\nAssistant: ", end="", flush=True)

            response = onemap_agent(user_input)

            # Print the response
            print(response.content)

            # If the response includes a static map, save it
            if hasattr(response, 'tool_results'):
                for tool_result in response.tool_results:
                    if tool_result.tool_name == 'get_static_map' and isinstance(tool_result.result, bytes):
                        filename = f"map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        with open(filename, 'wb') as f:
                            f.write(tool_result.result)
                        print(f"\n[Map saved to: {filename}]")

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            print(f"\nError: {e}")
            print("Please try again or type 'exit' to quit.")


def main():
    user_input = sys.stdin.read().strip()
    if user_input:
        response = onemap_agent(user_input)
        print(response)
    else:
        run_interactive_agent()


if not ONEMAP_ACCESS_TOKEN:
    if ONEMAP_REGISTERED_EMAIL and ONEMAP_REGISTERED_PASSWORD:
        token_data = get_onemap_access_token(ONEMAP_REGISTERED_EMAIL, ONEMAP_REGISTERED_PASSWORD)
        ONEMAP_ACCESS_TOKEN = token_data['access_token']
        print(f'Adding the following to .env')
        print(f'ONEMAP_ACCESS_TOKEN={ONEMAP_ACCESS_TOKEN}')
        with open('.env', 'a') as f:
            f.write(f'\nONEMAP_ACCESS_TOKEN={ONEMAP_ACCESS_TOKEN}\n')
    else:
        raise ValueError(
            "Access token not provided and ONEMAP_REGISTERED_EMAIL/"
            "ONEMAP_REGISTERED_PASSWORD environment variables not set"
        )


if __name__ == "__main__":
    main()
