from datetime import date, datetime
from nonebot import require, on_command
require("nonebot_plugin_alconna")

from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna import on_alconna, Arparma
from arclet.alconna import Alconna, Args
from db.model_dependencies import RestaurantBusiness
from services.restaurant_services.restaurant_order_services import (
    query_orders_service,
    query_history_order_service,
    generate_new_order_service,
    complete_order_service
)
from log.log_config.service_logger import info_logger

query_alc = Alconna(
    '/查看订单',
    Args["trade_date", datetime, date.today()],
)
query_cmd = on_alconna(query_alc, priority=1, block=True)


@query_cmd.handle()
async def query_order_endpoint(
    state: T_State,
    result: Arparma
) -> None:
    """
    查看当前未完成的订单

    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含日期
    """
    user_id = state.get('user_id')
    user_uid = state.get('user_uid')
    trade_date = result.get('trade_date')
    at_msg = MessageSegment.at(user_id=user_uid)
    try:
        waiting_orders = await query_orders_service(user_id=user_id)
        forward_msg = MessageSegment.node_custom(
            user_id=user_uid,
            nickname='今日订单',
            content='今日订单'
        )
        for order in waiting_orders:
            msg = f'订单编号: {order.order_id}\n获得比特: {order.byte}\n获得经验: {order.exp}\n过期时间: {order.expire_at}\n需要卡牌: {', '.join([f'{card_name * num}' for card_name, num in order.require_cards])}\n'
            node = MessageSegment.node_custom(
                user_id=user_id,
                nickname='今日订单',
                content=msg
            )
            forward_msg += node
        info_logger.info(f'success in query order. params: user_id={user_id}')
        await query_cmd.finish(forward_msg)
    
    except ValueError as e:
        info_logger.info(f'failed to query order. params: user_id={user_id}')
        if str(e) == 'restaurant not open':
            await query_cmd.finish('餐馆未开业，请使用 /开始营业' + at_msg)


async def query_history_order_endpoint():
    pass


async def generate_order_endpoint():
    pass


async def complete_order_endpoint():
    pass
