from typing import Optional, Literal
from nonebot import require, on_command
require("nonebot_plugin_alconna")

from arclet.alconna import Alconna, Args
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna import on_alconna, Arparma
from db.model_dependencies import RestaurantBusiness
from services.restaurant_services.restaurant_base_services import query_restaurant_info_service, change_main_business_service
from log.log_config.service_logger import info_logger


query_cmd = on_command('我的餐馆', priority=1, block=True)


@query_cmd.handle()
async def query_restaurant_endpoint(state: T_State) -> None:
    """
    查看个人餐馆信息接口
    :param state: 请求状态，用于获取玩家id
    """
    user_id = state.get('user_id')
    at_msg = MessageSegment.at(user_id=state.get('user_uid'))
    user_restaurant = await query_restaurant_info_service(user_id=user_id)
    if user_restaurant is None:
        await query_cmd.finish('您的餐馆还未开业，使用 /开业 开始经营餐馆吧' + at_msg)
    else:
        await query_cmd.finish(
            f'{at_msg}\n等级: {user_restaurant.level}\n主营业务: {user_restaurant.main_business.value}\n上次修改业务: {user_restaurant.last_change_business}\n开业时间: {user_restaurant.created_at}')


open_alc = Alconna(
    '/开业',
    Args["business", Literal['粤菜', '鲁菜', '川菜', '民族']],
)
open_cmd = on_alconna(open_alc, priority=1, block=True)


@open_cmd.handle()
async def open_business_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    开业接口

    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含餐馆主营业务
    """
    user_id = state.get('user_id')
    business = RestaurantBusiness(result.get('business'))
    at_msg = MessageSegment.at(user_id=state.get('user_uid'))
    
    if business is None or business == RestaurantBusiness.NOT_OPEN:
        return
    response = await change_main_business_service(
        user_id=user_id,
        business=business,
    )
    if response:
        info_logger.info(f'success in open business. params: user_id={user_id}, business={business}')
        await open_cmd.finish('开张大吉！' + at_msg)
    else:
        await open_cmd.finish('餐馆经营中，每个月只能修改一次主营业务哦。' + at_msg)
        info_logger.info(f'failed to open business. params: user_id={user_id}, business={business}')


change_alc = Alconna(
    '/修改业务',
    Args["business", Literal['粤菜', '鲁菜', '川菜', '民族']],
)
change_cmd = on_alconna(change_alc, priority=1, block=True)


@change_cmd.handle()
async def change_business_endpoint(
    state: T_State,
    result: Arparma
) -> None:
    """
    修改主营业务接口

    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含新的餐馆主营业务
    """
    user_id = state.get('user_id')
    business = RestaurantBusiness(result.get('business'))
    at_msg = MessageSegment.at(user_id=state.get('user_uid'))
    
    if business is None or business == RestaurantBusiness.NOT_OPEN:
        return
    response = await change_main_business_service(
        user_id=user_id,
        business=business,
    )
    if response:
        await change_cmd.finish('修改主营业务成功' + at_msg)
        info_logger.info(f'success in change business. params: user_id={user_id}, business={business}')
    else:
        await change_cmd.finish('餐馆经营中，每个月只能修改一次主营业务哦。' + at_msg)
        info_logger.info(f'failed to change business. params: user_id={user_id}, business={business}')
