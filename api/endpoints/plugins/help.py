"""
帮助插件 - 显示可用命令列表
"""
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, MessageSegment, ActionFailed
from core.config import settings, project_root
from config import allow_groups
from log.log_config.service_logger import info_logger

# 创建帮助命令处理器
help_cmd = on_command("help", priority=1, block=True)


@help_cmd.handle()
async def handle_help(event: MessageEvent):
    """
    处理 help 命令
    用法: /help
    功能: 显示所有可用命令及其说明
    """
    help_msg = """
🤖 NarcissusTCG(测试版)
━━━━━━━━━━━
⚙ bot管理
  /开始营业     - 启用游戏功能
  /小姚闭嘴     - 禁用游戏功能
  
📌 基础命令：
  /echo <内容>  - 复读
  /ping        - 测试在线
  /help        - 查看帮助
  
🎮 游戏功能：
  /注册           - 注册账号
  /签到           - 每日签到
  /个人信息 [@某人] - 查看玩家信息
  /我的卡牌 [卡牌包] [稀有度] [卡牌名]  - 查看卡牌收藏
  /抽卡 <卡牌包> [数量] - 抽卡，一次10比特
  /合成卡牌 <卡牌名> [数量] - 合卡
  /分解卡牌 <卡牌名> [数量] - 分卡
  /卡牌商店 [卡牌包] [稀有度] [卡牌名] [价格]  - 查看商店
  /上架卡牌 <卡牌名> [数量] [单价]  - 上架卡牌
  /下架卡牌 <商店编号> [数量]  - 下架卡牌
  /购买卡牌 <商店编号> [数量]  - 购买卡牌
  /查看卡牌 <卡牌名>  - 查看卡牌信息
  /卡牌图鉴 <卡牌包>  - 查看可收集卡牌

  卡牌包: base
  稀有度: 普通、稀有、史诗、传说、SP

💡 使用提示：
  - 命令前缀是 /
  - <>中必填，[]中可选填
━━━━━━━━━━━"""
    msg = MessageSegment.node_custom(
        user_id=settings.SUPER_USER_UID[0],
        nickname='姚云',
        content=help_msg
    )
    await help_cmd.send(msg)
    

start_cmd = on_command("开始营业", priority=1, block=True)


@start_cmd.handle()
async def start_help(
    bot: Bot,
    state: T_State,
) -> None:
    """
    启动TCG功能
    
    :param bot: 机器人对象，用于校验管理员
    :param state: 请求状态，存储了群号和用户qq号
    """
    group_id = state.get('group_id')
    user_uid = state.get('user_uid')

    if user_uid not in settings.SUPER_USER_UID:
        try:
            member_info = await bot.get_group_member_info(
                group_id=group_id,
                user_id=user_uid
            )
        except ActionFailed:
            return
        if member_info['role'] not in ['owner', 'admin']:
            return

    if group_id not in allow_groups:
        allow_groups.append(group_id)
        allow_groups_file = project_root / 'core' / 'ALLOW_GROUPS.json'
        with open(allow_groups_file, 'w', encoding='utf-8') as f:
            f.write(str(allow_groups))
        
        info_logger.info(f'start tcg service in {group_id}')
        await start_cmd.finish('开张开张，今天要赚它个盆满钵满！')
    else:
        await start_cmd.finish('小姚营业中，没有偷懒哦。')


shutdown_cmd = on_command("小姚闭嘴", priority=1, block=True)


@shutdown_cmd.handle()
async def shutup(
    bot: Bot,
    state: T_State
):
    """
    禁用TCG功能接口
    
    :param bot: 机器人对象，用于校验管理员
    :param state: 请求状态，存储了群号和用户qq号
    """
    group_id = state.get('group_id')
    user_uid = state.get('user_uid')
    if user_uid not in settings.SUPER_USER_UID:
        try:
            member_info = await bot.get_group_member_info(
                group_id=group_id,
                user_id=user_uid
            )
        except ActionFailed:
            return
        if member_info['role'] not in ['owner', 'admin']:
            return
    
    if group_id in allow_groups:
        allow_groups.remove(group_id)
        allow_groups_file = project_root / 'core' / 'ALLOW_GROUPS.json'
        with open(allow_groups_file, 'w', encoding='utf-8') as f:
            f.write(str(allow_groups))
        
        info_logger.info(f'close tcg service in {group_id}')
        await start_cmd.finish('小姚知道了 o(╥﹏╥)o ')
    else:
        await start_cmd.finish('才几点呀就要上班，小姚不要……')
            