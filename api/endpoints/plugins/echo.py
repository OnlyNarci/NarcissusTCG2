"""
回显插件示例 - 演示基本的命令处理
"""
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.params import CommandArg
from nonebot.typing import T_State

# 创建回显命令处理器
echo = on_command("echo", priority=5, block=True)


@echo.handle()
async def handle_echo(event: MessageEvent, args: Message = CommandArg()):
    """
    处理 echo 命令
    用法: /echo <内容>
    功能: 机器人会重复发送你发送的内容
    """
    # 获取命令参数
    msg = args.extract_plain_text()

    if msg:
        # 如果有参数，重复发送
        await echo.send(msg)
    else:
        # 如果没有参数，提示用法
        await echo.send("请输入要重复的内容，例如：/echo 你好")

# 创建打招呼命令
hello = on_command("hello", priority=10, block=True)


@hello.handle()
async def handle_hello(event: MessageEvent):
    """
    处理 hello 命令
    用法: /hello
    功能: 机器人会打招呼
    """
    # 获取发送者的昵称
    sender = event.sender.nickname or event.sender.card or "朋友"
    await hello.send(f"列国四海，千秋万载，都只有一个小姚")

# 创建 ping 命令
ping = on_command("ping", priority=10, block=True)


@ping.handle()
async def handle_ping(bot: Bot, event: MessageEvent, state: T_State):
    """
    处理 ping 命令
    用法: /ping
    功能: 测试机器人是否在线
    """
    await ping.send(f"pong!")
