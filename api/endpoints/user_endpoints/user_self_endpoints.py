from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from core.exceptions import ErrorCodes, ServerError
from services.user_services.user_self_services import create_user, get_user_info_service, check_in_service
from log.log_config.service_logger import info_logger, err_logger


auth_cmd = on_command('注册', priority=1, block=True)


@auth_cmd.handle()
async def register_user_endpoint(
    state: T_State,
) -> None:
    """
    用户注册
    
    :param state: 请求状态，用于获取玩家id
    """
    user_uid = state.get('user_uid')
    user_name = state.get('user_name')
    response = await create_user(
        user_uid=user_uid,
        user_name=user_name,
    )
    if response['success']:
        info_logger.info(f'user registered successfully: uid={user_uid}, name={user_name}')
        await auth_cmd.finish('注册成功，赠送5000比特，使用/help查看玩法。')
    else:
        await auth_cmd.finish('您已经注册过了。')
        info_logger.info(f'user registered failed, has registered before: uid={user_uid}, name={user_name}')


info_cmd = on_command('个人信息', priority=1, block=False)


@info_cmd.handle()
async def get_user_info_endpoint(
    state: T_State,
    msg: Message = CommandArg(),
) -> None:
    """
    用户查看个人信息
    
    :param state: 请求状态，用于获取玩家id
    :param msg: 个人信息后的参数，如果有@，获取首个被艾特对象的信息
    """
    at_qq_list = [seg.data["qq"] for seg in msg if seg.type == "at"]
    if at_qq_list:
        user_uid = at_qq_list[0]
    else:
        user_uid = state.get('user_uid')
        
    try:
        user_info_dict = await get_user_info_service(user_uid=user_uid)
        if user_info_dict['success']:
            user_info = user_info_dict['data']['user_info']
            info_logger.info(f'get user info success: user_uid={user_uid}')
            await info_cmd.send(f"玩家: {user_info.name}\n称号: {user_info.title}\n等级: {user_info.level}\n比特: {user_info.byte}\n主营业务: {user_info.main_business}")
        else:
            info_logger.info('get user info failed, user does not exist')
            await info_cmd.send('该玩家还没有注册。')
    
    except Exception as e:
        err_logger.error(f'get user info error: {e}')
        raise ServerError(error_code=ErrorCodes.InternalServerError)


check_in_cmd = on_command('签到', priority=1, block=True)


@check_in_cmd.handle()
async def check_in_endpoint(
    state: T_State,
) -> None:
    """
    签到接口
    
    :param state: 请求状态，用于获取玩家id
    """
    user_id = state.get('user_id')
    response = await check_in_service(user_id=user_id)
    if response['success']:
        msg = f'签到成功，获得{response['data']['add_byte']}比特。'
        if response['data']['continuous_check_in'] >= 3:
            msg += f'连续签到: {response['data']['continuous_check_in']}天，额外获得{response['data']['extra_byte']}比特'
        else:
            msg += '连续签到获取更多比特。'
        await check_in_cmd.finish(msg)
    else:
        await check_in_cmd.finish('您今天已经签到过了。')
