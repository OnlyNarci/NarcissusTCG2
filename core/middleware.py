from tortoise.exceptions import DoesNotExist
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor, event_postprocessor
from nonebot.message import run_preprocessor, run_postprocessor
from config import allow_groups
from core.exceptions import ClientError, ServerError, UnExceptError
from db.models import User
from api.dependencies.routes import tourist_routes
from log.log_config.service_logger import info_logger, err_logger


@event_preprocessor
async def temp_utils(
    bot: Bot,
    event: PrivateMessageEvent | GroupMessageEvent,
) -> None:
    """
    一些临时功能，用于回复不以/开头的消息
    
    :param bot:
    :param event:
    """
    message = event.get_message()
        
    message_text = message.extract_plain_text().strip()

    match message_text:
        case '小姚':
            await bot.send(event, '小姚在')
            return
        case '面粉袋子':
            await bot.send(event, '来自深渊的呼唤……')
            return


@event_preprocessor
async def get_user_id(
    bot: Bot,
    event: PrivateMessageEvent | GroupMessageEvent,
    state: T_State
) -> None:
    """
    记录请求，并从event中获取用户qq号(uid)，查询相应的用户id并存储与state中
    
    :param bot: 机器人实例，用于在用户未注册时返回提示
    :param event: 请求事件
    :param state: 请求全局对象
    """
    if not isinstance(event, (PrivateMessageEvent, GroupMessageEvent)):
        raise IgnoredException('非私聊/群聊消息事件，跳过用户信息预处理')      # 非私聊/群聊消息事件，跳过用户信息预处理
    
    message_text = event.get_message().extract_plain_text().strip()

    if not message_text.startswith('/'):
        raise IgnoredException('非请求机器人消息')      # 非请求机器人消息
    if len(message_text) > 50:
        await bot.send(event, '太长不看，肯定不是找我')
        raise IgnoredException('太长不看')
    
    user_uid = event.user_id
    state['user_uid'] = user_uid
    state['user_name'] = event.sender.nickname
    
    if isinstance(event, GroupMessageEvent):
        group_id = event.group_id
        state['group_id'] = group_id
        
        message_text_content = message_text[1:]
        if message_text_content.startswith(tuple(tourist_routes)):
            info_logger.info(f'got tourist request. prams: user_uid={user_uid}, message={message_text_content}')
            return  # 游客请求
        elif group_id not in allow_groups:
            raise IgnoredException('TCG功能禁用中，使用 /小姚开始营业 启用。')
        
    try:
        user = await User.get(uid=str(user_uid))
        state["user_id"] = user.id
    except DoesNotExist:
        await bot.send(event, '您还没有注册，请使用/注册 开始游戏')
        raise IgnoredException('游客请求非游客接口')      # 游客请求非游客接口，不再继续往下执行
    
    finally:
        info_logger.info(f'got request. prams: user_uid={user_uid}, user_id={state.get('user_id', 'Unregistered')}, message={message_text_content}')


@run_postprocessor
async def handle_exceptions(
    bot: Bot,
    event: Event,
    e: ClientError | ServerError | UnExceptError | Exception
) -> None:
    """
    处理事件响应中抛出的自定义异常，向机器人返回简洁信息
    :param bot: 机器人实例
    :param event: 事件对象
    :param e: 事件运行中抛出的异常
    """
    # 构建回复消息内容
    reply_msg = []
    
    match e:
        case ClientError() | ServerError():
            if e.message:
                reply_msg.append(e.message)
            if e.data:
                data_str = ", ".join([f"{k}: {v}" for k, v in e.data.items()])
                reply_msg.append(data_str)
        
        case UnExceptError():
            base_msg = "未知错误"
            if e.message:
                reply_msg.append(f"{base_msg}: {e.message}")
            else:
                reply_msg.append(base_msg)

            if e.data:
                data_str = ", ".join([f"{k}: {v}" for k, v in e.data.items()])
                reply_msg.append(data_str)
        
        case _:
            # 未捕获的异常
            err_msg = f"unexpected exception: {str(e)}"
            err_logger.error(err_msg)
            reply_msg.append("小姚被玩坏了")
    
    # 拼接最终回复内容
    final_msg = ", ".join(reply_msg) if reply_msg else "小姚被玩坏了"
    
    await bot.send(event, final_msg)
        