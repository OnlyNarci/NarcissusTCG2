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
from services.user_services.user_card_services import get_box_service, pull_card_service, compose_card_service, decompose_card_service
from log.log_config.service_logger import info_logger


box_cmd = on_command('我的卡牌', priority=1, block=True)


@box_cmd.handle()
async def get_box_endpoint(
    state: T_State,
    msg: Message = CommandArg(),
) -> None:
    """
    查看个人卡牌收藏
    
    :param state: 请求状态，用于获取玩家id
    :param msg: 查询参数, 可能包含卡牌包、卡牌稀有度、卡牌名包含字符串
    """
    # 拆分指令
    package = None
    card_rarity = None
    name_in = None
    for arg in msg.extract_plain_text().split():
        if arg in package_map:
            package = package_map[arg]
        elif arg in card_rarity_map:
            card_rarity = card_rarity_map[arg]
        else:
            name_in = arg
    
    # 调用服务层函数
    user_id = state.get('user_id')
    box = await get_box_service(
        user_id=user_id,
        name_in=name_in,
        rarity=card_rarity,
        package=package,
    )
    msg = '\n'.join([f"{card.name} * {card.number}" for card in box])
    
    forward_msg = MessageSegment.node_custom(
        user_id=state.get('user_uid'),
        nickname='卡牌收藏',
        content=msg
    )
    info_logger.info(f'success in get box: user_id={user_id}, package={package}, name_in={name_in}, rarity={card_rarity}')
    await box_cmd.finish(forward_msg)


pull_alc = Alconna(
    '/抽卡',
    Args["package", str],
    Args["number", int, 1],
)
pull_cmd = on_alconna(pull_alc, priority=1, block=True)


@pull_cmd.handle()
async def pull_card_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    抽卡接口
    
    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含扩展包名称和抽卡次数
    """
    package: Optional[str] = result.all_matched_args.get('package', None)
    if package is None:
        await pull_cmd.finish('请输入要抽取的卡牌包，例: /抽卡 base')
    try:
        package: Package = package_map[package.lower()]
    except KeyError:
        await pull_cmd.finish(f'未知卡包: {package}。')
        
    times: int = result.all_matched_args.get("number", 1)

    user_id = state.get('user_id')
    
    try:
        cards = await pull_card_service(
            user_id=user_id,
            package=package,
            times=times
        )
    except UnAtomicError as e:
        info_logger.info(f'failed to pull cards, cause {e.message}. prams: user_id={user_id}, package={package}, times={times}')
        await pull_cmd.finish(f'比特不足，需要{e.data.get('required_byte', None)}比特。')
        return
    
    msg = f'获得{times}张卡牌\n\n'
    msg += '\n'.join([f"{card.name} * {card.number}" for card in cards])
    
    forward_msg = MessageSegment.node_custom(
        user_id=state.get('user_uid'),
        nickname='获得卡牌',
        content=msg
    )
    info_logger.info(f'success in pull card. params: user_id={user_id}, package={package}, times={times}')
    await box_cmd.finish(forward_msg)


compose_alc = Alconna(
    '/合成卡牌',
    Args["card_name", str],
    Args["number", int, 1],
)
compose_cmd = on_alconna(compose_alc, priority=1, block=True)


@compose_cmd.handle()
async def compose_card_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    合卡接口
    
    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含目标合成卡牌和抽卡次数
    """
    user_id = state.get('user_id')
    user_uid = state.get('user_uid')
    at_msg = MessageSegment.at(user_id=user_uid)
    
    card_name: str = result.all_matched_args.get("card_name", "")
    if not card_name:
        await compose_cmd.finish(f'未知卡牌: {card_name}。')
    number: int = result.all_matched_args.get("number", 1)
    
    try:
        await compose_card_service(
            user_id=user_id,
            card_to_compose=card_name,
            number=number,
        )
        info_logger.info(f'success in compose card. params: user_id={user_id}, card_to_compose={card_name}, number={number}')
        await compose_cmd.finish(f'合成成功，获得卡牌: {card_name} * {number}。' + at_msg)
    except UnAtomicError as e:
        info_logger.info(f'failed to compose cards, cause {e.message}. params: user_id={state.get("user_id")}, card_name={card_name}, number={number}')
        match e.message:
            case 'card not found':
                await compose_cmd.finish(f'未知卡牌: {card_name}。' + at_msg)
            case 'not allow compose':
                await compose_cmd.finish(f'无法合成: {card_name}。' + at_msg)
            case 'level not enough':
                await compose_cmd.finish(f'等级不足，将在{e.data.get('unlock_level', 'unknown')}级解锁。' + at_msg)
            case 'materials not enough':
                msg = f'缺少卡牌\n'
                msg += '\n'.join([f"{card.name} * {card.number}" for card in e.data.get('lack_materials', [])])
                forward_msg = MessageSegment.node_custom(
                    user_id=user_id,
                    nickname='缺少材料',
                    content=msg
                )
                await box_cmd.finish(forward_msg)
            case _:
                await compose_cmd.finish('那真tmd见鬼了！' + at_msg)
                

decompose_alc = Alconna(
    '/分解卡牌',
    Args["card_name", str],
    Args["number", int, 1],
)
decompose_cmd = on_alconna(decompose_alc, priority=1, block=True)


@decompose_cmd.handle()
async def decompose_card_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    分卡接口
    
    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含目标分解卡牌和抽卡次数
    """
    card_name: str = result.all_matched_args.get("card_name", "")
    if not card_name:
        await compose_cmd.finish(f'未知卡牌: {card_name}。')
    number: int = result.all_matched_args.get("number", 1)
    
    user_id = state.get('user_id')
    
    try:
        user_cards = await decompose_card_service(
            user_id=user_id,
            card_to_decompose=card_name,
            number=number,
        )
        msg = f'分解成功，获得卡牌\n'
        msg += '\n'.join([f"{card.name} * {card.number}" for card in user_cards])
        forward_msg = MessageSegment.node_custom(
            user_id=user_id,
            nickname='获得卡牌',
            content=msg
        )
        info_logger.info(f'success in decompose card. params: user_id={user_id}, decompose_card={card_name}, number={number}')
        await box_cmd.finish(forward_msg)
        
    except UnAtomicError as e:
        info_logger.info(f'failed to decompose card, cause {e.message}. params: user_id={user_id}, decompose_card={card_name}, number={number}')
        match e.message:
            case 'card not found':
                await decompose_cmd.finish(f'未知卡牌: {card_name}')
            case 'not allow decompose':
                await decompose_cmd.finish(f'无法分解: {card_name}')
            case 'require card':
                await decompose_cmd.finish(f'卡牌未拥有: {card_name}')
            case _:
                raise ServerError(error_code=ErrorCodes.InternalServerError, message='真tmd见鬼了')
            
