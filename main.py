#!/usr/bin/env python3
import requests
import sys
import os
import json
from datetime import datetime

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

config = load_config()
user_conf = config.get("user", {})
LAT = user_conf.get("latitude", 35.71)
LON = user_conf.get("longitude", 139.81)
LOC_NAME = user_conf.get("location", "Unknown Location")

def get_weather():
    # 获取过去3天和未来4天（包含今天）的数据
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FTokyo&past_days=3&forecast_days=4"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data['daily']
    except Exception as e:
        print(f"获取天气失败: {e}")
        return None

def translate_weather_code(code):
    codes = {
        0: "晴朗", 1: "大部分晴朗", 2: "部分多云", 3: "阴天",
        45: "雾", 48: "雾", 51: "轻微毛毛雨", 53: "适中毛毛雨", 55: "密集毛毛雨",
        61: "轻微雨", 63: "适中雨", 65: "强降雨",
        71: "轻微雪", 73: "适中雪", 75: "强降雪",
        80: "轻微阵雨", 81: "适中阵雨", 82: "剧烈阵雨",
        95: "雷阵雨",
    }
    return codes.get(code, "未知")

def main():
    weather_data = get_weather()
    if not weather_data:
        return

    # 数据解析
    times = weather_data['time']
    max_temps = weather_data['temperature_2m_max']
    min_temps = weather_data['temperature_2m_min']
    weather_codes = weather_data['weathercode']
    prec_probs = weather_data['precipitation_probability_max']

    # 索引 3 是今天 (由于 past_days=3)
    today_idx = 3
    
    report = f"📊 {LOC_NAME} 天气趋势报告 ({times[today_idx]})\n"
    # 移除之前的 ====================
    report += "\n"

    # 1. 过去3天回顾
    report += "🕰️ 过去3天回顾:\n"
    for i in range(0, 3):
        report += f"   {times[i]}: {max_temps[i]}°C / {min_temps[i]}°C ({translate_weather_code(weather_codes[i])})\n"

    # 2. 今日天气
    report += f"\n✨ 今日天气 ({times[today_idx]}):\n"
    report += f"   状况: {translate_weather_code(weather_codes[today_idx])}\n"
    report += f"   气温: {max_temps[today_idx]}°C / {min_temps[today_idx]}°C\n"
    report += f"   降水概率: {prec_probs[today_idx]}%\n"

    # 3. 未来3天预报
    report += "\n🔮 未来3天预报:\n"
    for i in range(4, 7):
        report += f"   {times[i]}: {max_temps[i]}°C / {min_temps[i]}°C ({translate_weather_code(weather_codes[i])})\n"

    # 4. 气温趋势分析
    yesterday_temp = max_temps[today_idx - 1]
    today_temp = max_temps[today_idx]
    tomorrow_temp = max_temps[today_idx + 1]

    report += "\n📈 气温趋势分析:\n"
    diff_today = today_temp - yesterday_temp
    diff_tomorrow = tomorrow_temp - today_temp

    if diff_today > 1.5:
        report += f"   今天比昨天明显升温了 ({diff_today:+.1f}°C)。\n"
    elif diff_today < -1.5:
        report += f"   今天比昨天明显降温了 ({diff_today:+.1f}°C)。\n"
    else:
        report += "   气温与昨天相比变化不大。\n"

    if diff_tomorrow > 1.5:
        report += f"   提示：预计明天会进一步升温 ({diff_tomorrow:+.1f}°C)。\n"
    elif diff_tomorrow < -1.5:
        report += f"   提示：预计明天会明显变冷 ({diff_tomorrow:+.1f}°C)，注意保暖！\n"

    # 移除之前的 --------------------
    report += "\n"
    
    if prec_probs[today_idx] > 30:
        report += "💡 提醒：今天降水概率较高，请记得带伞。"
    
    # 保存到文件
    save_path = os.path.join(os.path.dirname(__file__), "daily_weather.txt")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"趋势报告已更新至: {save_path}")

if __name__ == "__main__":
    main()
