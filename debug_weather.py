#!/usr/bin/env python3
"""调试天气数据解析"""

def parse_weather_data(weather_text):
    """
    解析复杂的天气预报文本，提取关键信息
    """
    data = {
        'current_date': '',
        'current_condition': '',
        'current_high': None,
        'current_low': None,
        'current_precipitation': None,
        'previous_days': [],
        'future_days': [],
        'trend_analysis': ''
    }
    
    lines = weather_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 解析今日天气
        if '今日天气' in line and i + 1 < len(lines):
            j = i + 1
            while j < len(lines) and lines[j].strip() and not any(keyword in lines[j] for keyword in ['未来3天预报:', '气温趋势分析:', '----------------------------------------']):
                day_line = lines[j].strip()
                if '状况:' in day_line:
                    data['current_condition'] = day_line.split('状况:')[1].strip()
                elif '气温:' in day_line:
                    temp_part = day_line.split('气温:')[1].strip()
                    temps = temp_part.replace('°C', '').split('/')
                    if len(temps) >= 2:
                        try:
                            data['current_high'] = float(temps[0].strip())
                            data['current_low'] = float(temps[1].strip())
                        except:
                            pass
                elif '降水概率:' in day_line:
                    precip_part = day_line.split('降水概率:')[1].strip()
                    try:
                        data['current_precipitation'] = int(precip_part.replace('%', '').strip())
                    except:
                        pass
                j += 1
        
        # 解析过去几天的天气
        if '过去3天回顾:' in line:
            j = i + 1
            while j < len(lines) and lines[j].strip() and '未来3天预报:' not in lines[j]:
                day_line = lines[j].strip()
                if ':' in day_line and '(' in day_line:
                    try:
                        # 解析格式: 2026-01-29: 7.6°C / 0.9°C (大部分晴朗)
                        date_part = day_line.split(':')[0]
                        rest_part = ':'.join(day_line.split(':')[1:])
                        temp_part = rest_part.split('(')[0].strip()
                        condition_part = rest_part.split('(')[1].replace(')', '').strip()
                        
                        temps = temp_part.replace('°C', '').split('/')
                        if len(temps) >= 2:
                            prev_day = {
                                'date': date_part.strip(),
                                'high': float(temps[0].strip()),
                                'low': float(temps[1].strip()),
                                'condition': condition_part
                            }
                            data['previous_days'].append(prev_day)
                    except:
                        pass
                j += 1
        
        # 解析未来几天的天气
        if '未来3天预报:' in line:
            j = i + 1
            while j < len(lines) and lines[j].strip() and '气温趋势分析:' not in lines[j]:
                day_line = lines[j].strip()
                if ':' in day_line and '(' in day_line:
                    try:
                        # 解析格式: 2026-02-02: 9.0°C / 2.3°C (大部分晴朗)
                        date_part = day_line.split(':')[0]
                        rest_part = ':'.join(day_line.split(':')[1:])
                        temp_part = rest_part.split('(')[0].strip()
                        condition_part = rest_part.split('(')[1].replace(')', '').strip()
                        
                        temps = temp_part.replace('°C', '').split('/')
                        if len(temps) >= 2:
                            future_day = {
                                'date': date_part.strip(),
                                'high': float(temps[0].strip()),
                                'low': float(temps[1].strip()),
                                'condition': condition_part
                            }
                            data['future_days'].append(future_day)
                    except:
                        pass
                j += 1
        
        # 解析趋势分析
        if '气温趋势分析:' in line:
            data['trend_analysis'] = line.split('气温趋势分析:')[1].strip()
    
    return data


# 读取天气文件
with open('/home/tetsuya/weather.openclaw.lcmd/daily_weather.txt', 'r', encoding='utf-8') as f:
    weather_text = f.read().strip()

data = parse_weather_data(weather_text)

print("=== 解析结果 ===")
print(f"当前状况: {data['current_condition']}")
print(f"当前高温: {data['current_high']}")
print(f"当前低温: {data['current_low']}")
print(f"当前降水概率: {data['current_precipitation']}")
print(f"趋势分析: {data['trend_analysis']}")
print(f"过去几天: {data['previous_days']}")
print(f"未来几天: {data['future_days']}")

print("\n=== 温度判断 ===")
if data['current_high'] is not None:
    print(f"高温 {data['current_high']} 度")
    if data['current_high'] <= 5:
        print("-> 高于5度，添加保暖提醒")
    elif data['current_high'] <= 10:
        print("-> 高于10度，添加保暖提醒")
    elif data['current_high'] >= 25:
        print("-> 高于25度，添加降温提醒")

if data['current_low'] is not None:
    print(f"低温 {data['current_low']} 度")
    if data['current_low'] <= 0:
        print("-> 低于等于0度，添加防冻提醒")
    elif data['current_low'] <= 5:
        print("-> 低于等于5度，添加保暖提醒")

if data['current_low'] is not None and data['current_high'] is not None:
    temp_diff = data['current_high'] - data['current_low']
    print(f"温差: {temp_diff} 度")
    if temp_diff > 7:
        print("-> 温差大于7度，添加温差提醒")