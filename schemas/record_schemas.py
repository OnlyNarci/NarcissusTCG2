from typing import Dict
from datetime import datetime
from pydantic import Field
from db.model_dependencies import OrderStatus
from schemas import BaseParams


class StoreRecordParams(BaseParams):
    buyer_name: str = Field(default='您', min_length=1, max_length=20, title='买家名称')
    seller_name: str = Field(default='您', min_length=1, max_length=20, itle='卖家名称')
    card_name: str = Field(min_length=1, max_length=16, title='交易的卡牌名称')
    number: int = Field(ge=1, title='交易数量')
    price: int = Field(ge=1, title='交易单价')
    trade_time: datetime = Field(title='交易时间')
    
    
class OrderParams(BaseParams):
    """订单参数模型"""
    order_id: int = Field(ge=1, title='订单编号')
    require_cards: Dict[str, int] = Field(title='订单内容', description='键为卡牌名，值为卡牌数量')
    byte: int = Field(ge=0, title='订单价格', description='完成订单可以获得的比特')
    exp: int = Field(ge=0, title='经验值', description='完成订单获得')
    status: OrderStatus = Field(default=OrderStatus.WAITING, description='订单状态')
    expire_at: datetime = Field(title='订单过期时间')
    