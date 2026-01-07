from typing import Optional
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot_plugin_alconna import on_alconna, Arparma
from nonebot.adapters.onebot.v11 import MessageSegment
from arclet.alconna import Alconna, Args
from db.model_dependencies import Package, reverse_card_rarity_map
from core.exceptions import ErrorCodes, ServerError
from services.card_services.card_info_services import query_card_info_service, query_package_catalog_service
from log.log_config.service_logger import info_logger, err_logger


info_alc = Alconna(
    '/查看卡牌',
    Args["card_name", str],
)
info_cmd = on_alconna(info_alc, priority=1, block=True)


@info_cmd.handle()
async def query_card_info_endpoint(
    state: T_State,
    result: Arparma
) -> None:
    """
    用户注册
    
    :param state: 请求状态，用于解析用户信息
    :param result: 查询参数, 包含卡牌名
    """
    card_name: Optional[str] = result.all_matched_args.get('card_name', None)
    if card_name is None:
        await info_cmd.finish('请输入完整卡牌名称，例: /查看卡牌 面粉袋子')
        return
    
    card_params = await query_card_info_service(card_name=card_name)
    if card_params is None:
        info_logger.info(f'failed to get card info, cause: unknown card. params: user_id={state.get('user_id', 'unknown')}, card_name={card_name}')
        await info_cmd.finish(f'未知的卡牌: {card_name}。')
    else:
        msg = f'-- {card_params.name} --\n品质: {card_params.rarity}\n扩展包: {card_params.package}\n解锁等级: {card_params.unlock_level}\n趣闻: {card_params.description}\n'
        msg += '合成材料: '
        msg += ' '.join(f'{key}*{value}' for key, value in card_params.compose_materials.items())        # 拼接合成材料
        msg += '\n'
        msg += '分解获得: '
        msg += ' '.join(f'{key}*{value}' for key, value in card_params.decompose_materials.items())      # 拼接分解产物
        
        forward_msg = MessageSegment.node_custom(
            user_id=state.get('user_uid'),
            nickname='卡牌信息',
            content=msg
        )
        info_logger.info(f'success in get card info. params: user_id={state.get('user_id', 'unknown')}, card_name={card_name}')
        await info_cmd.finish(forward_msg)
    

catalog_alc = Alconna(
    '/卡牌图鉴',
    Args["package", str],
)
catalog_cmd = on_alconna(catalog_alc, priority=1, block=True)


@catalog_cmd.handle()
async def query_package_catalog_endpoint(
    state: T_State,
    result: Arparma
):
    """
    查看指定扩展包全卡牌图鉴
    :param state: 请求状态，用于解析用户信息
    :param result: 查询参数，包含卡包名
    """
    package = result.all_matched_args.get('package', None)
    try:
        package = Package(package)
        catalog = await query_package_catalog_service(package=package)
        info_logger.info(f'success in get package info. params: user_id={state.get('user_id')}, package={package}')
        if not catalog:
            await catalog_cmd.finish(f'扩展包未上线: {package}，敬请期待。')
        else:
            forward_msg = MessageSegment.node_custom(
                user_id=state.get('user_uid'),
                nickname='图鉴',
                content='\n'.join(catalog)
            )

            await catalog_cmd.finish(forward_msg)
    except ValueError:
        info_logger.info(f'failed to get package info, cause: unknown package. params: user_id={state.get('user_id')}, package={package}')
        await catalog_cmd.finish(f'未知的卡牌包: {package}。')
