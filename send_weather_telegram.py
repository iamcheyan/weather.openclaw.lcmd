#!/usr/bin/env python3
import os
import sys
import json
import requests
import subprocess

# Config
TELEGRAM_CHAT_ID = "7054611053"
WEATHER_SCRIPT = "/home/tetsuya/weather.openclaw.lcmd/weather_notifier.py"
WEATHER_CHART_SCRIPT = "/home/tetsuya/weather.openclaw.lcmd/weather_chart.py"
WEATHER_FILE = "/home/tetsuya/weather.openclaw.lcmd/daily_weather.txt"
WEATHER_IMAGE = "/home/tetsuya/weather.openclaw.lcmd/weather_trend.png"
CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")

def get_bot_token():
    # Try env var first
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        return token
    
    # Try config file
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            return cfg.get("channels", {}).get("telegram", {}).get("botToken")
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
    
    # Fallback to the known token if file read fails (User authorized use)
    return "8211541588:AAFUFT1BlylUumgGR3VMWSv4iJDJ-OUGfSA"

def get_weather_message():
    # Run the notifier script to get the formatted message
    try:
        result = subprocess.run(
            [sys.executable, WEATHER_SCRIPT, WEATHER_FILE],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error getting weather message: {e}", file=sys.stderr)
        return None

def generate_chart():
    try:
        subprocess.run([sys.executable, WEATHER_CHART_SCRIPT, WEATHER_FILE, WEATHER_IMAGE], check=True)
        return True
    except Exception as e:
        print(f"Error generating chart: {e}", file=sys.stderr)
        return False

def send_telegram_photo(photo_path, caption):
    token = get_bot_token()
    if not token: return False
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    # Telegram caption limit is 1024 characters.
    if len(caption) > 1024:
        # If too long, send empty caption and post text as separate message
        has_long_caption = True
        short_caption = ""
    else:
        has_long_caption = False
        short_caption = caption

    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': short_caption}
            resp = requests.post(url, data=payload, files=files, timeout=30)
            resp.raise_for_status()
        
        if has_long_caption:
            send_telegram_text(caption)
        
        return True
    except Exception as e:
        print(f"Error sending photo: {e}", file=sys.stderr)
        return False

def send_telegram_text(message):
    token = get_bot_token()
    if not token: return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=30).raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending text: {e}", file=sys.stderr)
        return False

def main():
    print("Starting weather notification with chart...")
    message = get_weather_message()
    if not message:
        print("Failed to generate weather message.")
        return

    generate_chart()
    
    if os.path.exists(WEATHER_IMAGE):
        print("Sending photo with caption...")
        send_telegram_photo(WEATHER_IMAGE, message)
    else:
        print("Chart not found, sending text only...")
        send_telegram_text(message)

if __name__ == "__main__":
    main()
