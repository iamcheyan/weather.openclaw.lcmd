#!/usr/bin/env python3
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import sys
import os
import json
from PIL import Image, ImageDraw, ImageFont

# 1. 加载配置与国际化
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f: return json.load(f)
    return {}

config = load_config()
lang = config.get("user", {}).get("language", "en")
loc_name = config.get("user", {}).get("location", "Tokyo")

I18N = {
    "zh": {"title": f"{loc_name} 天气趋势与预报", "today": "今天", "high": "最高温", "low": "最低温"},
    "en": {"title": f"{loc_name} Weather Trend & Forecast", "today": "Today", "high": "Max Temp", "low": "Min Temp"},
    "ja": {"title": f"{loc_name} 天気トレンドと予報", "today": "今日", "high": "最高気温", "low": "最低気温"}
}
t = I18N.get(lang, I18N["en"])

# 配置基础字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Noto Sans CJK JP', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False 

def get_weather_emoji(condition):
    if '雨' in condition: return '🌧️'
    if '雪' in condition: return '❄️'
    if '晴' in condition: return '☀️'
    if '阴' in condition: return '☁️'
    if '多云' in condition: return '⛅'
    if '雷' in condition: return '⛈️'
    return '🌈'

def parse_weather_data(weather_text):
    data_map = {}
    pattern_single = r'(\d{4}-\d{2}-\d{2})[:\s(]+([\d.]+)°?C?\s*/\s*([\d.]+)°?C?\s*\((.*?)\)'
    matches = re.findall(pattern_single, weather_text)
    for m in matches:
        date_obj = datetime.strptime(m[0], '%Y-%m-%d')
        data_map[date_obj] = {'high': float(m[1]), 'low': float(m[2]), 'cond': m[3]}
    
    today_date_match = re.search(r'今日天气 \((\d{4}-\d{2}-\d{2})\)', weather_text)
    today_cond_match = re.search(r'今日天气.*?状况:\s*(.*?)\n', weather_text, re.DOTALL)
    today_temp_match = re.search(r'今日天气.*?气温:\s*([\d.]+)°?C?\s*/\s*([\d.]+)°?C?', weather_text, re.DOTALL)
    
    if today_date_match and today_cond_match and today_temp_match:
        d_obj = datetime.strptime(today_date_match.group(1), '%Y-%m-%d')
        data_map[d_obj] = {'high': float(today_temp_match.group(1)), 'low': float(today_temp_match.group(2)), 'cond': today_cond_match.group(1).strip()}
            
    sorted_dates = sorted(data_map.keys())
    return sorted_dates, [data_map[d]['high'] for d in sorted_dates], \
           [data_map[d]['low'] for d in sorted_dates], [data_map[d]['cond'] for d in sorted_dates]

def create_chart(weather_file, output_file):
    if not os.path.exists(weather_file): return False
    with open(weather_file, 'r', encoding='utf-8') as f: content = f.read()
    dates, highs, lows, conds = parse_weather_data(content)
    if not dates: return False

    dpi = 120
    fig, ax = plt.subplots(figsize=(10, 5), facecolor='white', dpi=dpi)
    ax.set_facecolor('#fdfdfd')
    color_high, color_low = '#FF9F43', '#48DBFB'
    
    ax.plot(dates, highs, marker='o', markersize=6, color=color_high, linewidth=4, markerfacecolor='white', markeredgewidth=2, label=t['high'])
    ax.plot(dates, lows, marker='o', markersize=6, color=color_low, linewidth=4, markerfacecolor='white', markeredgewidth=2, label=t['low'])
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    for d in dates:
        if d.strftime('%Y-%m-%d') == today_str:
            ax.axvline(x=d, color='#666666', linestyle='--', linewidth=1, alpha=0.2)
            ax.text(d, min(lows) - 3.5, t['today'], ha='center', va='top', color='#2d3436', fontweight='bold', fontsize=12)
            break

    ax.fill_between(dates, highs, lows, color='#f0f0f0', alpha=0.3)
    
    for i, (h, l) in enumerate(zip(highs, lows)):
        ax.text(dates[i], h + 0.5, f'{int(h)}°', ha='center', va='bottom', color='#333333', fontweight='medium', fontsize=10)
        ax.text(dates[i], l - 0.5, f'{int(l)}°', ha='center', va='top', color='#333333', fontweight='medium', fontsize=10)

    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(dates, color='#666666', fontsize=10)
    plt.yticks([])
    plt.title(t['title'], color='#2d3436', fontsize=16, pad=50, fontweight='bold')
    plt.legend(loc='upper right', frameon=False)
    plt.ylim(min(lows) - 5, max(highs) + 12)
    plt.tight_layout()

    fig.canvas.draw()
    points_px = []
    for d, h in zip(dates, highs):
        px = ax.transData.transform((mdates.date2num(d), h))
        points_px.append(px)

    temp_base = output_file + ".base.png"
    plt.savefig(temp_base, dpi=dpi)
    plt.close()

    try:
        img = Image.open(temp_base).convert("RGBA")
        width, height = img.size
        emoji_font_path = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
        native_size, target_size = 109, 40
        fnt = ImageFont.truetype(emoji_font_path, native_size)
        
        for i, px in enumerate(points_px):
            emoji = get_weather_emoji(conds[i])
            x, y = int(px[0]), int(height - px[1])
            temp_emoji_img = Image.new("RGBA", (native_size + 20, native_size + 20), (0, 0, 0, 0))
            ImageDraw.Draw(temp_emoji_img).text((native_size // 2 + 10, native_size // 2 + 10), emoji, font=fnt, embedded_color=True, anchor="mm")
            resized_emoji = temp_emoji_img.resize((target_size, target_size), resample=Image.LANCZOS)
            img.alpha_composite(resized_emoji, (x - (target_size // 2), y - 90))
        
        img.save(output_file)
        if os.path.exists(temp_base): os.remove(temp_base)
        return True
    except Exception as e:
        if os.path.exists(temp_base): os.rename(temp_base, output_file)
        return False

if __name__ == "__main__":
    infile = sys.argv[1] if len(sys.argv) > 1 else "./daily_weather.txt"
    outfile = sys.argv[2] if len(sys.argv) > 2 else "./weather_trend.png"
    create_chart(infile, outfile)
