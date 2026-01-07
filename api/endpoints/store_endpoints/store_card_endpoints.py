from pydantic import ValidationError
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna import on_alconna, Arparma
from arclet.alconna import Alconna, Args
from core.exceptions import UnAtomicError
from db.model_dependencies import card_rarity_map, package_map
from schemas.card_schemas import StoreCardParams
from services.store_services.store_card_services import query_store_service, list_card_service, delist_card_service, buy_card_service
from log.log_config.service_logger import info_logger, err_logger


query_cmd = on_command('卡牌商店', priority=1, block=True)


@query_cmd.handle()
async def query_store_endpoint(
    state: T_State,
    msg: Message = CommandArg(),
) -> None:
    """
    查询商店接口
    
    :param state: 请求状态，用于获取玩家id
    :param msg: 解析的请求参数，可能包含扩展包名称、卡牌名称、最大价格
    """
    # 拆分指令
    package = None
    card_rarity = None
    name_in = None
    price_le = None
    for arg in msg.extract_plain_text().split():
        if arg in package_map:
            package = package_map[arg]
        elif arg in card_rarity_map:
            card_rarity = card_rarity_map[arg]
        else:
            try:
                price_le = int(arg)
            except ValueError:
                name_in = arg
                
    user_id = state.get('user_id')
    cards = await query_store_service(
        user_id=user_id,
        name_in=name_in,
        card_rarity=card_rarity,
        package=package,
        price_le=price_le
    )
    user_uid = state.get('user_uid')
    node1 = MessageSegment.node_custom(
        user_id=user_uid,
        nickname='卡牌商店',
        content='在售卡牌'
    )
    msg = '编号   卡牌   单价   数量   卖家\n'
    msg += '\n'.join([f"{card.store_id}  {card.name}  {card.price}  {card.number}  {card.owner_name}" for card in cards])
    node2 = MessageSegment.node_custom(
        user_id=user_uid,
        nickname='卡牌商店',
        content=msg
    )

    forward_msg = node1 + node2
    
    info_logger.info(f'success in get store. params: user_id={user_id}, name_in={name_in}, rarity={card_rarity}')
    await query_cmd.finish(forward_msg)


list_alc = Alconna(
    '/上架卡牌',
    Args["card_name", str],
    Args["number", int, 1],
    Args["price", int, 1000],
)
list_cmd = on_alconna(list_alc, priority=1, block=True)


@list_cmd.handle()
async def list_card_endpoint(
    state: T_State,
    result: Arparma
) -> None:
    """
    上架卡牌接口

    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含卡牌名称、上架数量、挂单价格
    """
    user_id = state.get('user_id')
    
    card_name = result.all_matched_args.get('card_name', "")
    number = result.all_matched_args.get('number', 1)
    price = result.all_matched_args.get('price', 1000)
    try:
        card_to_list = StoreCardParams(
            name=card_name,
            number=number,
            price=price
        )
    except ValidationError as e:
        info_logger.error(f'failed to list card, cause: {e}. params: user_id={user_id}, card_name={card_name}, number={number}, price={price}')
        await list_cmd.finish('请输入正确指令。例: /上架卡牌 木块')
        return
    
    try:
        store_card_id = await list_card_service(
            user_id=user_id,
            card_to_list=card_to_list,
        )
        info_logger.info(f'success in list card. params: user_id={user_id}, card_name={card_name}, number={number}, price={price}')
        await list_cmd.finish(f'成功上架卡牌: {card_name} * {number}。\n编号: {store_card_id}\n单价{price}')
    except UnAtomicError:
        info_logger.info(f'failed to list card, cause: card not enough. params: user_id={user_id}, card_name={card_name}, number={number}, price={price}')
        await list_cmd.finish('主厨您好像没有这么多卡牌呢。')
        

delist_alc = Alconna(
    '/下架卡牌',
    Args["store_id", int],
    Args["number", int, 0],
)
delist_cmd = on_alconna(delist_alc, priority=1, block=True)


@delist_cmd.handle()
async def delist_card_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    下架卡牌接口

    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含商店id
    """
    user_id = state.get('user_id')
    
    store_id = result.all_matched_args.get('store_id', None)
    if store_id is None:
        await delist_cmd.finish('请输入要下架卡牌的商店编号，例: /下架卡牌 1')
    number = result.all_matched_args.get('number', 0)
    
    try:
        card_to_delist = StoreCardParams(
            store_id=store_id,
            number=number,
        )
    except ValidationError as e:
        info_logger.error(f'failed to delist card, cause: {str(e)}. params: user_id={user_id}, store_id={store_id}, number={number}')
        await delist_cmd.finish('请输入正确指令，例: /下架卡牌 1')
        return
    
    try:
        card_name, delist_num = await delist_card_service(
            user_id=user_id,
            card_to_delist=card_to_delist,
        )
        info_logger.info(f'success in delist card. params: user_id={user_id}, store_id={store_id}, number={delist_num}')
        await delist_cmd.finish(f'成功下架卡牌: {card_name} * {delist_num}。')
    except UnAtomicError:
        info_logger.info(f'failed to delist card, cause: card not enough. params: user_id={user_id}, store_id={store_id}, number={number}')
        await delist_cmd.finish('卡牌不见踪迹，我也无能为力(可能已被其他玩家购买，请查看交易记录)。')
        

buy_alc = Alconna(
    '/购买卡牌',
    Args["store_id", int],
    Args["number", int, 1],
)
buy_cmd = on_alconna(buy_alc, priority=1, block=True)


@buy_cmd.handle()
async def buy_card_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    购买卡牌接口

    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含商店id、购买数量
    """
    user_id = state.get('user_id')
    
    store_id = result.all_matched_args.get('store_id', None)
    if store_id is None:
        await buy_cmd.finish('请输入要购买卡牌的商店编号，例: /购买卡牌 1')
    number = result.all_matched_args.get('number', 1)
    
    try:
        card_to_buy = StoreCardParams(
            store_id=store_id,
            number=number,
        )
    except ValidationError as e:
        info_logger.error(f'failed to buy card, cause: {str(e)}. params: user_id={user_id}, store_id={store_id}, number={number}')
        await buy_cmd.finish('请输入正确指令，例: /购买卡牌 1')
        return
    
    try:
        need_byte, card_name = await buy_card_service(
            user_id=user_id,
            card_to_buy=card_to_buy,
        )
        info_logger.info(f'success in buy card. params: user_id={user_id}, store_id={store_id}, number={number}')
        await buy_cmd.finish(f'成功购买卡牌: {card_name} * {number}，消耗 {need_byte} 比特。')
    except UnAtomicError as e:
        info_logger.info(f'failed to buy card, cause: {e.message}. params: user_id={user_id}, store_id={store_id}, number={number}')
        match e.message:
            case 'card not found':
                await buy_cmd.finish('卡牌不见踪迹，我也无能为力。')
            case 'can not buy self card':
                await buy_cmd.finish('无法购买自己上架的卡牌，请使用 /下架卡牌。')
            case 'trade today too march':
                await buy_cmd.finish('今天您已经买了太多卡牌啦，休息一下吧~')
            case 'user byte not enough':
                await buy_cmd.finish('比特好像不够了呢。')
            case 'user level not enough':
                await buy_cmd.finish('您还没有解锁这张卡牌。')
            case _:
                await buy_cmd.finish('那真tmd见鬼了！')
