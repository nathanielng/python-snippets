#!/usr/bin/env python

import os
import requests

from strands import tool
from typing import Dict, Any, Optional

# Get API key from environment variable for security
# You should set this with: export OPENWEATHERMAP_API_KEY="your_api_key"
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', None)

@tool
def get_current_weather(lat: float, lon: float, units: str = 'metric', api_key: Optional[str] = None) -> Dict[Any, Any]:
    """
    Get current weather data for a specific location.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        units: Units of measurement. Options: 'standard', 'metric', or 'imperial'
        api_key: OpenWeatherMap API key (optional, will use env var if not provided)
    
    Returns:
        Dictionary containing current weather data
    """
    key = api_key or API_KEY
    if not key:
        raise ValueError("OpenWeatherMap API key not found. Set OPENWEATHERMAP_API_KEY environment variable or provide api_key parameter.")
    
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': key,
        'units': units
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@tool
def get_hourly_forecast(lat: float, lon: float, units: str = 'metric', cnt: int = 96, api_key: Optional[str] = None) -> Dict[Any, Any]:
    """
    Get hourly weather forecast for 4 days (96 hours).
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        units: Units of measurement. Options: 'standard', 'metric', or 'imperial'
        cnt: Number of timestamps to return (max 96 for 4 days)
        api_key: OpenWeatherMap API key (optional, will use env var if not provided)
    
    Returns:
        Dictionary containing hourly forecast data
    """
    key = api_key or API_KEY
    if not key:
        raise ValueError("OpenWeatherMap API key not found. Set OPENWEATHERMAP_API_KEY environment variable or provide api_key parameter.")
    
    url = f"https://pro.openweathermap.org/data/2.5/forecast/hourly"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': key,
        'units': units,
        'cnt': min(cnt, 96)  # Ensure we don't exceed the maximum
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

@tool
def get_forecast_3hour(lat: float, lon: float, units: str = 'metric', cnt: int = 40, api_key: Optional[str] = None) -> Dict[Any, Any]:
    """
    Get 3-hour step weather forecast for 5 days (40 timestamps).
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        units: Units of measurement. Options: 'standard', 'metric', or 'imperial'
        cnt: Number of timestamps to return (max 40 for 5 days)
        api_key: OpenWeatherMap API key (optional, will use env var if not provided)
    
    Returns:
        Dictionary containing 3-hour forecast data
    """
    key = api_key or API_KEY
    if not key:
        raise ValueError("OpenWeatherMap API key not found. Set OPENWEATHERMAP_API_KEY environment variable or provide api_key parameter.")
    
    url = f"https://api.openweathermap.org/data/2.5/forecast"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': key,
        'units': units,
        'cnt': min(cnt, 40)  # Ensure we don't exceed the maximum
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
