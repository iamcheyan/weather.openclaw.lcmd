#!/bin/bash

# ==========================================
# Weather.OpenClaw.LCMD Setup Script
# ==========================================

set -e

INSTALL_DIR=$(pwd)
PYTHON_EXECUTABLE=$(which python3)

echo "🚀 Starting installation in $INSTALL_DIR..."

# 1. 检查并安装 Python 依赖
echo "📦 Checking dependencies..."
if ! $PYTHON_EXECUTABLE -c "import matplotlib, PIL" &> /dev/null; then
    echo "Installing matplotlib and Pillow..."
    $PYTHON_EXECUTABLE -m pip install matplotlib pillow --break-system-packages || \
    $PYTHON_EXECUTABLE -m pip install matplotlib pillow
else
    echo "Dependencies already satisfied."
fi

# 2. 动态修正脚本中的绝对路径
echo "🔧 Configuring local paths..."
# 将脚本中所有的 /home/tetsuya/weather.openclaw.lcmd/ 替换为当前的安装路径
find "$INSTALL_DIR" -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" \) -exec sed -i "s|/home/tetsuya/weather.openclaw.lcmd/|$INSTALL_DIR/|g" {} +

# 3. 设置权限
chmod +x "$INSTALL_DIR/send_weather_telegram.py"
chmod +x "$INSTALL_DIR/weather_notifier.py"
chmod +x "$INSTALL_DIR/weather_chart.py"

# 4. 辅助引导：Telegram 配置
echo "------------------------------------------"
echo "✅ Installation complete!"
echo ""
echo "📝 Next Steps for Agents/Humans:"
echo "1. Configure your Telegram Bot Token and Chat ID in:"
echo "   $INSTALL_DIR/send_weather_telegram.py"
echo "   (Or ensure ~/.openclaw/openclaw.json is present)"
echo ""
echo "2. Add the following to your crontab (crontab -e):"
echo "   35 6 * * * $PYTHON_EXECUTABLE $INSTALL_DIR/send_weather_telegram.py"
echo ""
echo "3. Test the system:"
echo "   $PYTHON_EXECUTABLE $INSTALL_DIR/send_weather_telegram.py"
echo "------------------------------------------"
