#!/usr/bin/env python

"""
A module for retrieving and querying Singapore carpark availability data.

This module provides functionality to:
- Fetch real-time carpark availability data from data.gov.sg API
- Query available lots for specific carparks and lot types
- Get lists of all carpark numbers and lot types
- Interact with the data through a conversational AI agent

The module uses the Strands framework to create an AI assistant that can answer
queries about carpark availability in natural language.

Functions:
    get_carpark_data(): Fetches raw carpark data from the API
    get_available_lots(carpark_number, lot_type): Gets available lots for a specific carpark
    get_carpark_numbers(): Gets list of all carpark numbers
    get_lot_types(): Gets list of all lot types
    main(): Entry point for running the carpark agent

Dependencies:
    - requests
    - strands
    - json

Lot Types
    - C: Car
    - H: Heavy Vehicle
    - M: Minibus
    - L: Lorry
    - Y: Motorcycle
    - S: Special Vehicle
"""

import json
import logging
import requests

from strands import Agent, tool
from strands.models import BedrockModel
from typing import Dict, List, Union

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger('strands').setLevel(logging.INFO)


def get_carpark_data():
    url = 'https://api.data.gov.sg/v1/transport/carpark-availability'
    response = requests.get(url).json()
    # print(json.dumps(response, indent=2, default=str))

    items = response.get('items', [])
    if not len(items):
        return None

    carpark_data = items[0].get('carpark_data')
    if not len(carpark_data):
        return None

    data = []
    for item in carpark_data:
        carpark_info = item.get('carpark_info')
        carpark_number = item.get('carpark_number')
        update_datetime = item.get('update_datetime')
        if not carpark_info:
            print(f'Skipping item: {item}')
            break
            continue
        for lots in carpark_info:
            lot_type = lots['lot_type']
            lots_available = lots['lots_available']
            total_lots = lots['total_lots']
            data.append({
                'lots_available': lots_available,
                'total_lots': total_lots,
                'lot_type': lot_type,
                'carpark_number': carpark_number,
                'update_datetime': update_datetime
            })
    return data


@tool
def get_available_lots(carpark_number: str, lot_type: str = 'C') -> Union[List[Dict], str]:
    """
    Get available parking lots for a specific carpark and optionally filter by lot type.

    Args:
        carpark_number (str): The carpark number to query (e.g. 'HE12')
        lot_type (str, optional): Type of parking lot to filter by. Valid values are:
            - C: Car
            - H: Heavy Vehicle  
            - M: Minibus
            - L: Lorry
            - Y: Motorcycle
            - S: Special Vehicle
            Defaults to 'C' for car.

    Returns:
        Union[Dict, str]: Dictionary containing carpark data if found:
            {
                'lots_available': int,  # Number of available lots
                'total_lots': int,      # Total number of lots
                'lot_type': str,        # Type of parking lot
                'carpark_number': str,  # Carpark identifier
                'update_datetime': str  # Last update timestamp
            }
            Or string 'No carparks found' if no matching data
    """

    carpark_data = [item for item in carpark_data if item['carpark_number'] == carpark_number]
    logger.info(f'Found {len(carpark_data)} carparks for {carpark_number}')

    if len(carpark_data):
        if lot_type:
            carpark_data = [item for item in carpark_data if item['lot_type'] == lot_type]

        if len(carpark_data):
            logger.info(f'Carpark Data: {carpark_data[0]}')
            return carpark_data[0]
        else:
            return 'No carparks found'
    else:
        return 'No carparks found'


@tool
def get_carpark_numbers() -> str:
    """
    Get a list of all available carpark numbers from the carpark data.

    Returns:
        str: A comma-separated string of unique carpark numbers
    """
    carpark_numbers = [item['carpark_number'] for item in carpark_data]
    return ', '.join(list(set(carpark_numbers)))


@tool
def get_lot_types() -> List[str]:
    """
    Get a list of all available carpark lot types.

    Returns:
        list: A list of unique lot type codes as strings:
            - C: Car
            - H: Heavy Vehicle
            - M: Minibus 
            - L: Lorry
            - Y: Motorcycle
            - S: Special Vehicle
    """
    lot_types = [item['lot_type'] for item in carpark_data]
    return list(set(lot_types))  # return unique values


carpark_data = get_carpark_data()


SYSTEM_PROMPT = """
You are a helpful assistant that provides information about carpark availability in Singapore. You can check the number of available lots in a specific carpark by providing the carpark number. You can also filter by lot type (e.g. "C" for car, "Y" for motorcycle, "H" for heavy vehicle).

To get started:
1. Use get_carpark_numbers() to see a list of available carparks
2. Use get_lot_types() to see available lot types
3. Use get_available_lots(carpark_number, lot_type) to check availability for a specific carpark
   - carpark_number is required
   - lot_type is optional (C=car, Y=motorcycle, H=heavy vehicle)

Please provide the carpark number when asking about availability.
"""

# model_id = 'us.anthropic.claude-sonnet-4-20250514-v1:0'
model_id = 'us.amazon.nova-pro-v1:0'
carpark_agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    model=BedrockModel(model_id=model_id),
    tools=[get_available_lots,get_carpark_numbers,get_lot_types]
)

examples = [
    'What are the carpark lot types?',
    'What are the carpark numbers?',
    'What are the available lots for carpark HE12?'
]

def main():
    # print(json.dumps(carpark_data, indent=2, default=str))
    carpark_agent(examples[2])


if __name__ == '__main__':
    main()
