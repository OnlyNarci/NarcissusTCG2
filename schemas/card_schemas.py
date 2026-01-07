from typing import Optional, Dict
from pydantic import Field
from schemas import BaseParams
from db.model_dependencies import Package, CardRarity


class CardParams(BaseParams):
    """
    卡牌基本模型
    """
    card_id: Optional[int] = Field(default=None, ge=1, title='卡牌id')
    name: Optional[str] = Field(default=None, max_length=16, title='卡牌名称')
    image: Optional[str] = Field(default=None, min_length=0, max_length=1024, title='卡牌原画')
    rarity: Optional[CardRarity] = Field(default=None, title='卡牌稀有度')
    package: Package = Field(default=Package.BASE, max_length=16, title='卡牌包')
    unlock_level: Optional[int] = Field(default=None, ge=1, title='解锁等级')
    compose_materials: Dict[str, int] = Field(default={}, title='合成材料', description='键为卡牌名，值为数量')
    decompose_materials: Dict[str, int] = Field(default={}, title='分解产物', description='键为卡牌名，值为数量')
    description: Optional[str] = Field(default=None, title='卡牌描述')
    
    def __repr__(self):
        return f'<UserCardParams (card_id={self.card_id}; name={self.name}; image={self.image}; rarity={self.rarity}; package={self.package})>'
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, CardParams):
            return False
        return self.card_id == other.card_id

    
class StoreCardParams(CardParams):
    """
    商店中的卡牌模型，用于校验查商店、买卡、上架卡牌的请求参数
    """
    store_id: Optional[int] = Field(default=None, ge=1, title='卡牌的商店id')
    number: int = Field(default=1, ge=0, title='卡牌数量')
    price: int = Field(default=1000, ge=0, title='卡牌价格')
    owner_name: str = Field(default="unknown", title='卡牌持有者名称')
    
    def __repr__(self):
        return f'<UserCardParams (card_id={self.card_id}; name={self.name}; image={self.image}; rarity={self.rarity}; package={self.package}; store_id={self.store_id}; number={self.number}; price={self.price}; is_publish={self.is_publish})>'
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, StoreCardParams):
            return False
        return self.store_id == other.store_id
    
    
class UserCardParams(CardParams):
    """
    玩家卡牌模型，用于校验合卡、分卡的请求参数
    """
    user_name: Optional[str] = Field(default=None, min_length=1, max_length=20, title='卡牌数量')
    user_uid: Optional[int] = Field(default=None, ge=1, title='用户uid')
    number: Optional[int] = Field(default=None, ge=1, title='卡牌数量')
    
    def __repr__(self):
        return f'<UserCardParams (card_id={self.card_id}; name={self.name}; image={self.image}; rarity={self.rarity}; package={self.package}; number={self.number})>'

    
if __name__ == '__main__':
    pass
    