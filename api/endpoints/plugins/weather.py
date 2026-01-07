"""
天气查询插件示例 - 演示网络请求和数据获取
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message


weather = on_command("weather", priority=10, block=True)


@weather.handle()
async def handle_weather(event: MessageEvent, args: Message = CommandArg()):
    """
    处理 weather 命令
    用法: /weather <城市名>
    功能: 查询指定城市的天气（示例使用模拟数据）
    """
    city = args.extract_plain_text().strip()

    if not city:
        await weather.send("请输入城市名称，例如：/weather 北京")
        return

    weather_data = await get_weather_mock(city)

    if weather_data:
        msg = f"""
🌤️ {weather_data['city']} 天气
━━━━━━━━━━━━━
📅 日期: {weather_data['date']}
🌡️ 温度: {weather_data['temperature']}°C
☁️ 天气: {weather_data['weather']}
💧 湿度: {weather_data['humidity']}%
💨 风力: {weather_data['wind']}
━━━━━━━━━━━━━
"""
        await weather.send(msg)
    else:
        await weather.send(f"抱歉，没有找到城市「{city}」的天气信息")


async def get_weather_mock(city: str) -> dict:
    """
    模拟获取天气数据（示例函数）
    实际使用时应该调用真实的天气 API
    """
    # 模拟一些城市的天气数据
    mock_data = {
        "北京": {
            "city": "北京",
            "date": "2026-01-03",
            "temperature": "5",
            "weather": "晴",
            "humidity": "45",
            "wind": "北风3级"
        },
        "上海": {
            "city": "上海",
            "date": "2026-01-03",
            "temperature": "12",
            "weather": "多云",
            "humidity": "65",
            "wind": "东南风2级"
        },
        "广州": {
            "city": "广州",
            "date": "2026-01-03",
            "temperature": "20",
            "weather": "小雨",
            "humidity": "80",
            "wind": "微风"
        }
    }

    return mock_data.get(city)

# 创建今日日期命令
date = on_command("date", priority=10, block=True)


@date.handle()
async def handle_date(event: MessageEvent):
    """
    处理 date 命令
    用法: /date
    功能: 显示今天的日期和时间
    """
    from datetime import datetime

    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    time_str = now.strftime("%H:%M:%S")
    weekday = now.strftime("%A")

    # 英文星期转换为中文
    weekday_map = {
        "Monday": "星期一",
        "Tuesday": "星期二",
        "Wednesday": "星期三",
        "Thursday": "星期四",
        "Friday": "星期五",
        "Saturday": "星期六",
        "Sunday": "星期日",
    }
    weekday_cn = weekday_map.get(weekday, weekday)

    await date.send(f"📅 今天是 {date_str} {weekday_cn}\n⏰ 当前时间: {time_str}")
