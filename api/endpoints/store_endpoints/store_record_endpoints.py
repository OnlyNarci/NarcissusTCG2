from datetime import datetime, date
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_alconna import on_alconna, Arparma
from arclet.alconna import Alconna, Args
from services.store_services.store_record_services import query_trade_record_service
from log.log_config.service_logger import info_logger


query_alc = Alconna(
    '/交易记录',
    Args["trade_date", datetime, date.today()],
)
query_cmd = on_alconna(query_alc, priority=1, block=True)


@query_cmd.handle()
async def query_trade_record_endpoint(
    state: T_State,
    result: Arparma,
) -> None:
    """
    查看指定日期的交易记录接口
    
    :param state: 请求状态，用于获取玩家id
    :param result: 解析的请求参数，包含交易日
    """
    user_id = state.get('user_id')
    user_uid = state.get('user_uid')
    trade_date = result.all_matched_args.get('trade_date')
    if trade_date is None:
        trade_date = date.today()
    else:
        trade_date = trade_date.date()
    
    store_record = await query_trade_record_service(
        user_id=user_id,
        trade_date=trade_date,
    )
    msg1 = f'购买记录 {trade_date}\n\n'
    msg1 += '\n'.join([f'{record.buyer_name} 在 {record.trade_time.strftime('%H:%M')}向 {record.seller_name} 购买了 {record.card_name}*{record.number}，单价 {record.price} 比特。' for record in store_record['buy_records']])
    node1 = MessageSegment.node_custom(
        user_id=user_uid,
        nickname='交易记录',
        content=msg1
    )
    
    msg2 = f'出售记录 {trade_date}\n\n'
    msg2 += '\n'.join([f'{record.buyer_name} 在 {record.trade_time.strftime('%H:%M')} 向 {record.seller_name} 购买了 {record.card_name}*{record.number}，单价 {record.price} 比特。' for record in store_record['sell_records']])
    node2 = MessageSegment.node_custom(
        user_id=user_uid,
        nickname='交易记录',
        content=msg2
    )
    
    forward_msg = node1 + node2
    
    info_logger.info(f'success in get store record. params: user_id={user_id}, trade_date={trade_date}')
    await query_cmd.finish(forward_msg)
    