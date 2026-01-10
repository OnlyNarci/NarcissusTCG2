from enum import IntEnum, StrEnum


class FriendshipStatus(IntEnum):
    """
    好友状态
    """
    WAITING = 0     # 等待同意
    CONFIRM = 1     # 已经是好友
    BLACK_LIST = 2  # 黑名单


class CardRarity(IntEnum):
    """
    卡牌稀有度
    """
    COMMON = 1       # 普通
    RARE = 2         # 稀有
    EPIC = 3         # 史诗
    LEGENDARY = 4    # 传说
    SPECIAL = 5      # 特殊卡牌


card_rarity_map = {
    '普通': CardRarity.COMMON,
    '稀有': CardRarity.RARE,
    '史诗': CardRarity.EPIC,
    '传说': CardRarity.LEGENDARY,
    'SP': CardRarity.SPECIAL
}
# 各品质卡牌的内在价值
card_worth = {
    CardRarity.COMMON: 7,
    CardRarity.RARE: 21,
    CardRarity.EPIC: 63,
    CardRarity.LEGENDARY: 189
}
reverse_card_rarity_map = {
    1: '普通',
    2: '稀有',
    3: '史诗',
    4: '传说',
    5: 'SP'
}


class OrderStatus(IntEnum):
    """
    订单状态
    """
    WAITING = 0     # 待完成
    CONFIRM = 1     # 已完成
    

class GroupMemberStatus(IntEnum):
    """
    群成员状态
    """
    BLACK_LIST = 0      # 黑名单
    UNDER_REVIEW = 1    # 申请中
    MEMBER = 2          # 普通成员
    ADMIN = 3           # 管理员
    OWNER = 4           # 群主


class MessageType(IntEnum):
    TEXT = 0
    IMAGE = 1
    LINK = 2
    NOTICE = 3


class RestaurantBusiness(StrEnum):
    NOT_OPEN = '未开业'
    SOUTH_FLAVOR = '粤菜'     # 华南地区菜品
    NORTH_FLAVOR = '鲁菜'     # 华北地区菜品
    BASHU_FLAVOR = '川菜'     # 云贵川地区菜品
    ETHNIC_FLAVOR = '民族'    # 少数民族特色菜品
    
    
restaurant_map = {
    '未开业': RestaurantBusiness.NOT_OPEN,
    '粤菜': RestaurantBusiness.SOUTH_FLAVOR,
    '鲁菜': RestaurantBusiness.NORTH_FLAVOR,
    '川菜': RestaurantBusiness.BASHU_FLAVOR,
    '民族': RestaurantBusiness.ETHNIC_FLAVOR
}


class Package(StrEnum):
    BASE = 'base'
    SOUTH_FLAVOR = '粤菜'
    NORTH_FLAVOR = '鲁菜'
    BASHU_FLAVOR = '川菜'
    ETHNIC_FLAVOR = '民族'
    
    
package_map = {
    'base': Package.BASE,
    '华南风味': Package.SOUTH_FLAVOR,
    '京鲁风味': Package.NORTH_FLAVOR,
    '巴蜀风味': Package.BASHU_FLAVOR,
    '民族风味': Package.ETHNIC_FLAVOR
}
    

class City(StrEnum):
    """城市枚举类型"""
    LIGHTING_HARBOR = 'LightingHarbor'
    

class TaskStatus(IntEnum):
    """任务枚举类型"""
    WAITING = 0
    CONFIRM = 1
    TIMEOUT = 2
    