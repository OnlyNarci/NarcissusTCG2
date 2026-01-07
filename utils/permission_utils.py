from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from log.log_config.service_logger import err_logger


async def is_group_admin_or_owner(bot: Bot, event: GroupMessageEvent) -> bool:
    """
    校验用户是否是群管理员/群主
    :param bot: Bot实例
    :param event: 群消息事件
    :return: True=是管理员/群主，False=不是
    """
    try:
        # 调用OneBot V11接口获取群成员信息
        member_info = await bot.get_group_member_info(
            group_id=event.group_id,
            user_id=event.user_id
        )
        # role字段：owner=群主，admin=管理员，member=普通成员
        return member_info["role"] in ["owner", "admin"]
    except Exception as e:
        err_logger.error(f"校验群权限失败 - 群号:{event.group_id}, 用户:{event.user_id}, 错误:{str(e)}")
        return False
    