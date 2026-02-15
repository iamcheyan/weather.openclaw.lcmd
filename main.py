#!/usr/bin/env python3
import requests
import sys
import os
import json
from datetime import datetime
import holidays

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
LANG = user_conf.get("language", "zh")
COUNTRY = user_conf.get("country", "JP")

def get_weather():
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
    if not weather_data: return

    geo_holidays = holidays.CountryHoliday(COUNTRY)

    times = weather_data['time']
    max_temps = weather_data['temperature_2m_max']
    min_temps = weather_data['temperature_2m_min']
    weather_codes = weather_data['weathercode']
    prec_probs = weather_data['precipitation_probability_max']

    today_idx = 3
    report = f"📊 {LOC_NAME} 天气趋势报告 ({times[today_idx]})\n\n"

    # 1. 过去3天回顾
    report += "🕰️ 过去3天回顾:\n"
    for i in range(0, 3):
        dt = datetime.strptime(times[i], '%Y-%m-%d').date()
        h_name = geo_holidays.get(dt)
        suffix = f" [{h_name}]" if h_name else ""
        report += f"   {times[i]}: {max_temps[i]}°C / {min_temps[i]}°C ({translate_weather_code(weather_codes[i])}){suffix}\n"

    # 2. 今日天气
    dt_today = datetime.strptime(times[today_idx], '%Y-%m-%d').date()
    h_today = geo_holidays.get(dt_today)
    h_suffix = f" (祝日: {h_today})" if h_today else ""
    
    report += f"\n✨ 今日天气 ({times[today_idx]}):\n"
    report += f"   状况: {translate_weather_code(weather_codes[today_idx])}{h_suffix}\n"
    report += f"   气温: {max_temps[today_idx]}°C / {min_temps[today_idx]}°C\n"
    report += f"   降水概率: {prec_probs[today_idx]}%\n"

    # 3. 未来3天预报
    report += "\n🔮 未来3天预报:\n"
    for i in range(4, 7):
        dt_f = datetime.strptime(times[i], '%Y-%m-%d').date()
        h_f = geo_holidays.get(dt_f)
        f_suffix = f" [{h_f}]" if h_f else ""
        report += f"   {times[i]}: {max_temps[i]}°C / {min_temps[i]}°C ({translate_weather_code(weather_codes[i])}){f_suffix}\n"

    # 4. 气温趋势分析
    yesterday_temp = max_temps[today_idx - 1]
    today_temp = max_temps[today_idx]
    tomorrow_temp = max_temps[today_idx + 1]
    report += "\n📈 气温趋势分析:\n"
    diff_today = today_temp - yesterday_temp
    diff_tomorrow = tomorrow_temp - today_temp
    if diff_today > 1.5: report += f"   今天比昨天明显升温了 ({diff_today:+.1f}°C)。\n"
    elif diff_today < -1.5: report += f"   今天比昨天明显降温了 ({diff_today:+.1f}°C)。\n"
    else: report += "   气温与昨天相比变化不大。\n"

    if diff_tomorrow > 1.5: report += f"   提示：预计明天会进一步升温 ({diff_tomorrow:+.1f}°C)。\n"
    elif diff_tomorrow < -1.5: report += f"   提示：预计明天会明显变冷 ({diff_tomorrow:+.1f}°C)，注意保暖！\n"

    report += "\n"
    if h_today:
        report += f"🍵 提醒：今天是祝日「{h_today}」，工作先放放，好好休息一下吧。\n"
    if prec_probs[today_idx] > 30:
        report += "💡 提醒：今天降水概率较高，请记得带伞。\n"
    
    save_path = os.path.join(os.path.dirname(__file__), "daily_weather.txt")
    with open(save_path, "w", encoding="utf-8") as f: f.write(report)
    print(f"趋势报告同步假期完成: {save_path}")

if __name__ == "__main__":
    main()
