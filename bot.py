"""
NoneBot2 QQ 机器人启动入口
"""
import nonebot
nonebot.init()
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter
from nonebot.adapters.console import Adapter as ConsoleAdapter
from tortoise import Tortoise
from core.middleware import *
from core.config import TORTOISE_ORM_CONFIG
from config import driver


driver.register_adapter(OneBotV11Adapter)
driver.register_adapter(ConsoleAdapter)

nonebot.load_plugins("api/endpoints/plugins")
nonebot.load_plugins("api/endpoints/user_endpoints")
nonebot.load_plugins("api/endpoints/store_endpoints")
nonebot.load_plugins("api/endpoints/card_endpoints")
nonebot.load_plugins("api/endpoints/restaurant_endpoints")


@driver.on_startup
async def on_startup():
    await Tortoise.init(config=TORTOISE_ORM_CONFIG)
    print('数据库已连接')
    print("=" * 50)
    print("NoneBot2 QQ Bot 已启动!")
    print("=" * 50)
    print("机器人配置:")
    print(f"  监听地址: {driver.config.host}:{driver.config.port}")
    print(f"  超级用户: {driver.config.superusers}")
    print(f"  命令前缀: {driver.config.command_start}")
    print(f"  WebSocket URLs: {driver.config.onebot_ws_urls}")
    print("=" * 50)


@driver.on_shutdown
async def close_tortoise():
    await Tortoise.close_connections()
    print("✅ Tortoise-ORM 数据库连接已断开")


if __name__ == "__main__":
    # 启动机器人
    nonebot.run()
    