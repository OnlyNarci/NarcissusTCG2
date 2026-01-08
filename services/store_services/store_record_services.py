from datetime import datetime, timedelta, date
from typing import List, Dict

from db.models import StoreRecord
from schemas.record_schemas import StoreRecordParams


async def query_trade_record_service(
    user_id: int,
    trade_date: date
) -> Dict[str, List[StoreRecordParams]]:
    """
    获取玩家自己指定日期的交易记录
    :param user_id: 玩家id
    :param trade_date: 日期
    """
    # 1. 构造时间范围：目标日期 00:00:00 到次日 00:00:00
    start_datetime = datetime.combine(trade_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(days=1)

    # 2. 筛选条件：用户ID + 时间范围
    buy_records = await StoreRecord.filter(
        buyer_id=user_id,
        created_at__gte=start_datetime,
        created_at__lt=end_datetime
    ).select_related('seller', 'card').all()
    
    sell_records = await StoreRecord.filter(
        seller_id=user_id,
        created_at__gte=start_datetime,
        created_at__lt=end_datetime
    ).select_related('buyer', 'card').all()

    # 3. 转换为返回参数格式
    return {
        'buy_records': [
            StoreRecordParams(
                seller_name=record.seller.name,
                card_name=record.card.name,
                number=record.number,
                price=record.price,
                trade_time=record.created_at
            )
            for record in buy_records
        ],
        'sell_records': [
            StoreRecordParams(
                buyer_name=record.buyer.name,
                card_name=record.card.name,
                number=record.number,
                price=record.price,
                trade_time=record.created_at
            )
            for record in sell_records
        ]
    }
