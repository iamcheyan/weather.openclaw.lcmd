#!/usr/bin/env python3
"""
个性化天气提醒脚本
根据天气预报信息生成个性化的提醒建议
"""

import re


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
        if '今日天气' in line:
            j = i + 1
            while j < len(lines) and lines[j].strip() and '未来3天预报:' not in lines[j]:
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
            # 收集从气温趋势分析开始直到文档结束的所有行
            j = i
            trend_parts = []
            while j < len(lines):
                if j == i:
                    # 第一行，去掉"气温趋势分析:"前缀
                    trend_part = line.split('气温趋势分析:')[1].strip()
                    if trend_part:
                        trend_parts.append(trend_part)
                else:
                    # 后续行，直接添加
                    if j < len(lines) and not lines[j].strip():
                        break
                    trend_parts.append(lines[j].strip())
                j += 1
            
            data['trend_analysis'] = ' '.join(trend_parts)
    
    return data


def generate_personalized_weather_advice(weather_text):
    """
    根据天气预报文本生成个性化提醒
    """
    data = parse_weather_data(weather_text)
    advice_lines = []
    
    # 分析今日天气
    if data['current_precipitation'] is not None:
        if data['current_precipitation'] >= 70:
            advice_lines.append("⚠️ 今日降水概率很高，强烈建议携带雨具！")
        elif data['current_precipitation'] >= 40:
            advice_lines.append("☔ 今日可能有雨，建议携带雨具以防万一。")
        elif data['current_precipitation'] >= 20:
            advice_lines.append("🌦️ 今日降水概率较低，但备把伞总是好的。")
    
    # 分析今日温度
    if data['current_high'] is not None:
        if data['current_high'] <= 5:
            advice_lines.append("🧥 气温较低，注意保暖，穿厚外套。")
        elif data['current_high'] <= 10:
            advice_lines.append("🧣 今天较冷，建议增加衣物。")
        elif data['current_high'] >= 25:
            advice_lines.append("☀️ 气温较高，注意防晒，穿轻薄衣物。")
    
    if data['current_low'] is not None:
        if data['current_low'] <= 0:
            advice_lines.append("🧊 夜间气温接近或低于冰点，注意防冻。")
        elif data['current_low'] <= 5:
            advice_lines.append("🌙 早晚温差大，注意添衣保暖。")
    
    # 如果高温较低（低于15度）且温差较大，提醒注意保暖
    if data['current_high'] is not None and data['current_low'] is not None:
        temp_difference = data['current_high'] - data['current_low']
        if data['current_high'] < 15 and temp_difference > 7:
            advice_lines.append("🌡️ 今日温差较大，请注意适时增减衣物。")
        elif temp_difference > 10:
            advice_lines.append("🌡️ 今日温差很大，请特别注意适时增减衣物。")
    
    # 根据天气状况提醒
    if data['current_condition']:
        condition_lower = data['current_condition'].lower()
        if '雪' in data['current_condition'] or '雪fall' in condition_lower:
            advice_lines.append("🌨️ 今日有雪，出行请注意道路湿滑，小心慢行。")
        elif '雨' in data['current_condition'] or 'rain' in condition_lower:
            advice_lines.append("💧 注意雨水可能影响视线，驾驶请减速慢行。")
        elif '雾' in data['current_condition'] or 'fog' in condition_lower:
            advice_lines.append("🌫️ 有雾天气，能见度较低，外出请注意安全。")
        elif '晴朗' in data['current_condition'] or 'clear' in condition_lower:
            advice_lines.append("🌞 天气晴朗，适合户外活动或晾晒衣物。")
        elif '阴天' in data['current_condition'] or 'overcast' in condition_lower:
            advice_lines.append("☁️ 阴天为主，光线较暗，注意照明。")
        elif '多云' in data['current_condition'] or 'cloudy' in condition_lower:
            advice_lines.append("⛅ 多云天气，温度适宜，适合外出活动。")
        elif '部分' in data['current_condition'] or 'partly' in condition_lower:
            advice_lines.append("🌤️ 部分多云，天气良好，适合户外活动。")
    
    # 分析趋势和对比
    if data['trend_analysis']:
        trend_lower = data['trend_analysis'].lower()
        if '降温' in data['trend_analysis'] or '下降' in data['trend_analysis'] or '降' in data['trend_analysis']:
            advice_lines.append("📉 根据趋势分析，今天有降温，注意适当增添衣物。")
        elif '升温' in data['trend_analysis'] or '上升' in data['trend_analysis'] or '升' in data['trend_analysis'] or '+' in trend_lower:
            advice_lines.append("📈 根据趋势分析，今天有升温，注意适时减少衣物。")
        elif '比昨天' in data['trend_analysis'] and ('升温' in data['trend_analysis'] or '+' in trend_lower):
            advice_lines.append("📈 今天比昨天明显升温，注意适时减少衣物。")
        elif '比昨天' in data['trend_analysis'] and ('降温' in data['trend_analysis'] or '-' in trend_lower):
            advice_lines.append("📉 今天比昨天降温，注意适当增添衣物。")
    
    # 分析未来几天的天气
    if data['future_days']:
        next_few_days_highs = [day['high'] for day in data['future_days']]
        next_few_days_lows = [day['low'] for day in data['future_days']]
        next_few_days_conditions = [day['condition'] for day in data['future_days']]
        
        # 检查未来几天是否有显著降温
        if data['current_high'] and next_few_days_highs:
            avg_future_high = sum(next_few_days_highs) / len(next_few_days_highs)
            if data['current_high'] - avg_future_high > 3:  # 当天比未来几天平均高3度以上
                advice_lines.append("📉 未来几天气温将逐渐下降，请提前准备保暖衣物。")
        
        # 检查未来几天是否有显著升温
        if data['current_high'] and next_few_days_highs:
            avg_future_high = sum(next_few_days_highs) / len(next_few_days_highs)
            if avg_future_high - data['current_high'] > 3:  # 未来几天比当天高3度以上
                advice_lines.append("📈 未来几天气温将逐渐升高，注意调整穿着。")
        
        # 检查未来几天的降水情况
        rain_indicators = ['雨', '雪', 'rain', 'snow', 'shower', 'storm']
        rainy_days = [day for day in data['future_days'] if any(indicator in day['condition'].lower() for indicator in rain_indicators)]
        if rainy_days:
            # 找到第一个下雨的日子
            for day in data['future_days']:
                if any(indicator in day['condition'].lower() for indicator in rain_indicators):
                    advice_lines.append(f"🗓️ {day['date']} 预计有降水，如需外出请提前准备雨具。")
                    break
    
    # 整合原天气预报和个性化建议
    final_message = weather_text
    if advice_lines:
        final_message += f"\n\n📋 个人提醒:\n"
        for advice in advice_lines:
            final_message += f"{advice}\n"
    
    return final_message


def main():
    """读取天气文件并生成个性化提醒"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python weather_notifier.py <weather_file_path>")
        return
    
    weather_file_path = sys.argv[1]
    
    try:
        with open(weather_file_path, 'r', encoding='utf-8') as f:
            weather_text = f.read().strip()
        
        personalized_message = generate_personalized_weather_advice(weather_text)
        print(personalized_message)
        
    except FileNotFoundError:
        print(f"Error: Weather file not found at {weather_file_path}")
    except Exception as e:
        print(f"Error reading weather file: {e}")


if __name__ == "__main__":
    main()