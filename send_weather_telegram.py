#!/usr/bin/env python3
import os
import sys
import json
import requests
import subprocess

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

config = load_config()

# 动态配置项
TELEGRAM_CHAT_ID = config.get("telegram", {}).get("chatId", "")
WEATHER_SCRIPT = os.path.join(os.path.dirname(__file__), "weather_notifier.py")
CHART_SCRIPT = os.path.join(os.path.dirname(__file__), "weather_chart.py")
WEATHER_FILE = config.get("paths", {}).get("daily_weather", "./daily_weather.txt")
IMAGE_FILE = config.get("paths", {}).get("weather_trend_image", "./weather_trend.png")

def get_bot_token():
    token = config.get("telegram", {}).get("botToken")
    if token: return token
    # Fallback to OpenClaw system config
    try:
        sys_config = os.path.expanduser("~/.openclaw/openclaw.json")
        if os.path.exists(sys_config):
            with open(sys_config, 'r') as f:
                data = json.load(f)
                return data.get("channels", {}).get("telegram", {}).get("botToken")
    except: pass
    return None

def main():
    token = get_bot_token()
    if not token or not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN or CHAT_ID not found.")
        return

    print("Starting weather notification with chart...")
    
    # 1. 生成图表
    try:
        subprocess.run([sys.executable, CHART_SCRIPT, WEATHER_FILE, IMAGE_FILE], check=True)
    except Exception as e:
        print(f"Error generating chart: {e}")

    # 2. 生成文字建议
    try:
        process = subprocess.Popen([sys.executable, WEATHER_SCRIPT, WEATHER_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        caption, _ = process.communicate()
    except Exception as e:
        caption = "今日天气预报已更新，请查看图表。"

    # 3. 发送 Telegram 消息 (图片 + 文案)
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    if os.path.exists(IMAGE_FILE):
        print("Sending photo with caption...")
        with open(IMAGE_FILE, "rb") as photo:
            files = {"photo": photo}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = requests.post(url, files=files, data=data)
    else:
        print("Image not found, sending text only...")
        url_text = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url_text, data={"chat_id": TELEGRAM_CHAT_ID, "text": caption})

if __name__ == "__main__":
    main()
