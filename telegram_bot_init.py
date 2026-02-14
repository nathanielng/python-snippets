"""
Telegram Bot Initialization Script

Fetches updates from Telegram bot API, extracts the chat ID from the first message,
saves updates to updates.json, and sends a test message to the chat.

Setup Instructions:
1. Get your Telegram Bot API Key:
   - Open Telegram and search for @BotFather
   - Start a chat and send /newbot
   - Follow the prompts to choose a name and username for your bot
   - BotFather will provide your API key (format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)
   
2. Start your bot:
   - Go to https://t.me/yourbotusername (replace with your bot's username)
   - Click "Start" to activate the bot
   - Send a test message to your bot
   
3. Get your Chat ID:
   - Set the environment variable: export TELEGRAM_API_KEY='your_api_key_here'
   - Run this script to retrieve the chat ID from the first message

Requires TELEGRAM_API_KEY environment variable to be set.
"""

import json
import os
import requests
import sys


def get_api_key():
    api_key = os.environ.get('TELEGRAM_API_KEY')
    if not api_key:
        print("Error: TELEGRAM_API_KEY environment variable not set")
        sys.exit(1)
    return api_key


def fetch_updates(api_key):
    try:
        response = requests.get(f"https://api.telegram.org/bot{api_key}/getUpdates", timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Error: Failed to get updates from Telegram: {e}")
        sys.exit(1)
    
    if not data.get("ok") or not data.get("result"):
        print("Error: No updates found or invalid response from Telegram")
        sys.exit(1)
    
    return data


def save_updates(data):
    try:
        with open("updates.json", "w") as f:
            json.dump(data, f)
    except IOError as e:
        print(f"Error: Failed to write updates.json: {e}")
        sys.exit(1)


def extract_chat_id(data):
    try:
        return data["result"][0]["message"]["chat"]["id"]
    except (KeyError, IndexError):
        print("Error: Could not extract chat ID from response")
        sys.exit(1)


def send_test_message(api_key, chat_id):
    try:
        response = requests.get(f"https://api.telegram.org/bot{api_key}/sendMessage",
                               params={"chat_id": chat_id, "text": "Test message"}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error: Failed to send message: {e}")
        sys.exit(1)


def main():
    api_key = get_api_key()
    data = fetch_updates(api_key)
    save_updates(data)
    chat_id = extract_chat_id(data)
    send_test_message(api_key, chat_id)
    
    print("\n✅ Bot initialization successful!")
    print(f"✅ Chat ID: {chat_id}")
    print("✅ Test message sent")


if __name__ == "__main__":
    main()
