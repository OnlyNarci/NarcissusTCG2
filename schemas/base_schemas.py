from typing import Dict
from datetime import datetime
from pydantic import Field
from schemas import BaseParams
from schemas.card_schemas import UserCardParams
from db.model_dependencies import RestaurantBusiness


class UserParams(BaseParams):
    """用户个人参数模型"""
    uid: int = Field(ge=1, title='用户uid')
    name: str = Field(max_length=20, title='用户姓名')
    title: str = Field(max_length=20, title='用户称号')
    level: int = Field(default=1, ge=1, title='等级')
    byte: int = Field(ge=0, title='玩家持有比特')
    exp: int = Field(ge=0, default=0, title='玩家当前经验点数')
    require_exp: int = Field(ge=1000, default=1000, title='升到下一级所需经验点数')
    main_business: RestaurantBusiness = Field(title='主营业务')


class OrderParams(BaseParams):
    """订单参数模型"""
    order_id: int = Field(ge=1, title='订单编号')
    require_cards: Dict[str, int] = Field(title='订单内容', description='键为卡牌名，值为卡牌数量')
    byte: int = Field(ge=0, title='订单价格', description='完成订单可以获得的比特')
    exp: int = Field(ge=0, title='经验值', description='完成订单获得')
    expire_at: datetime = Field(title='订单过期时间')
