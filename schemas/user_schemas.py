from datetime import date
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
    

class RestaurantParams(BaseParams):
    """餐馆信息模型"""
    level: int = Field(default=1, ge=1, title='等级')
    main_business: RestaurantBusiness = Field(title='主营业务')
    last_change_business: date = Field(title='上一次修改主营业务的日期')
    created_at: date = Field(title='开业日期')
