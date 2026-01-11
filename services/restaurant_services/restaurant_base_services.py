from typing import Optional
from datetime import date
from tortoise.exceptions import DoesNotExist
from db.models import Restaurant
from db.model_dependencies import RestaurantBusiness
from schemas.user_schemas import RestaurantParams


async def query_restaurant_info_service(
    user_id: int,
) -> Optional[RestaurantParams]:
    """
    查看玩家个人餐厅经营信息
    
    :param user_id: 玩家id
    
    :return: 未开业返回None, 已开业返回餐馆信息
    """
    try:
        user_restaurant = await Restaurant.get(user_id=user_id)
        if user_restaurant.main_business == RestaurantBusiness.NOT_OPEN:
            return None
        else:
            return RestaurantParams(
                level=user_restaurant.level,
                main_business=user_restaurant.main_business,
                last_change_business=user_restaurant.last_change_business,
                created_at=user_restaurant.created_at,
            )
    except DoesNotExist:
        return None


async def change_main_business_service(
    user_id: int,
    business: RestaurantBusiness,
) -> bool:
    """
    餐馆开业/餐馆修改主营业务通用后端服务
    
    :param user_id: 用户id
    :param business: 期望修改的新业务
    
    :return: 成功修改/创建返回True，否则返回False
    """
    today = date.today()
    try:
        user_restaurant = await Restaurant.get(user_id=user_id)
        if user_restaurant.main_business != business and (today - user_restaurant.last_change_business).day > 30:
            user_restaurant.main_business = business
            user_restaurant.last_change_business = today
            await user_restaurant.save()
            return True

    except DoesNotExist:
        await Restaurant.create(
            user_id=user_id,
            main_business=business,
            last_change_business=today,
        )
        return True
    
    return False
