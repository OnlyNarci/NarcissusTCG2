from typing import Optional
from nonebot import require, on_command
require("nonebot_plugin_alconna")

from arclet.alconna import Alconna, Args
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna import on_alconna, Arparma
from core.exceptions import ErrorCodes, UnAtomicError, ServerError
from db.model_dependencies import Package, card_rarity_map, package_map
from services.user_services.user_order_services import query_orders_service, complete_order_service
from log.log_config.service_logger import info_logger


query_cmd = on_command('查看订单', priority=1, block=True)


