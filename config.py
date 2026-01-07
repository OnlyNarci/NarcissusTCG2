"""
NoneBot2 QQ 机器人配置文件
"""
import json
from nonebot import get_driver
from core.config import project_root


# 获取驱动实例
driver = get_driver()

# WebSocket 连接配置
driver.config.onebot_ws_urls = ["ws://127.0.0.1:3001"]

# 插件配置
driver.config.log_level = "INFO"  # 日志级别: DEBUG, INFO, WARNING, ERROR

# 会话超时时间（秒）
driver.config.session_expire_timeout = 120

allow_groups_file = project_root / 'core' / 'ALLOW_GROUPS.json'
f = open(allow_groups_file, 'r', encoding='utf-8')
allow_groups: list = json.load(f)
f.close()
