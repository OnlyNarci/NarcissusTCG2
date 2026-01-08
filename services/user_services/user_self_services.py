import random
from datetime import date, timedelta
from tortoise.transactions import atomic
from tortoise.exceptions import IntegrityError, DoesNotExist
from db.models import User
from db.model_dependencies import RestaurantBusiness
from schemas.base_schemas import UserParams
from self_types.service_type import ServiceResponse


async def create_user(
    user_name: str,
    user_uid: int,
) -> ServiceResponse:
    """
    注册功能
    
    :param user_name: 用户名
    :param user_uid: 用户qq号
    
    :return: 注册是否成功，失败返回原因
    :return type:
        {
            'success': bool,
            'message': str,
        }
    """

    try:
        await User.create(
            uid=user_uid,
            name=user_name,
            byte=5000
        )
        return {
            'success': True,
            'message': '注册成功'
        }
    except IntegrityError:
        return {
            'success': False,
            'message': '已经注册'
        }


async def get_user_info_service(
    user_uid: int,
) -> ServiceResponse:
    """
    返回用户个人信息
    
    :param user_uid: 用户qq号
    
    :return: 用户个人信息模型
    :return type:
        {
            'success': bool,
            'message': str,
            'data': {
                'user_info': Optional[UserParams]
            }
        }
    """
    try:
        user = await User.get(uid=str(user_uid))
    except DoesNotExist:
        return {
            'success': False,
            'message': 'user does not exist',
            'data': {
                'user_info': None
            }
        }

    restaurant = await user.restaurant.all().first()
    return {
        'success': True,
        'message': 'success in getting user info',
        'data': {
            'user_info': UserParams(
                uid=user.uid,
                name=user.name,
                title=user.title,
                level=user.level,
                byte=user.byte,
                main_business=restaurant.main_business if restaurant is not None else RestaurantBusiness.NOT_OPEN
            )
        }
    }


@atomic()
async def check_in_service(
    user_id: int
) -> ServiceResponse:
    """
    签到服务【纯Python原生版，无numpy依赖】

    :param user_id: 用户id
    :return: 本次签到实际增加的byte数量
    """
    MIN_ADD = 200
    MAX_ADD = 400
    BASE_MEAN = 210
    LEVEL_COEFF = 1
    STD_DEV = 8
    
    today = date.today()
    yesterday = today - timedelta(days=1)  # 昨日日期
    
    # 查询用户，并确保今日未签到
    user = await User.get(id=user_id)
    if user.last_check_in == today:
        return {
            'success': False,
            'message': 'has check in today'
        }
    
    if user.last_check_in == yesterday:
        user.continuous_check_in += 1
    else:
        user.continuous_check_in = 1
    
    user.last_check_in = today
        
    mean = BASE_MEAN + (max(user.level, 1) * LEVEL_COEFF)
    add_byte = random.gauss(mean, STD_DEV)
    add_byte = max(MIN_ADD, min(int(round(add_byte)), MAX_ADD))
    
    extra_byte = 0
    if user.continuous_check_in >= 30:
        extra_byte += 40      # 连续签到30天，额外+20byte
    elif user.continuous_check_in >= 7:
        extra_byte += 20      # 连续签到7天，额外+10byte
    elif user.continuous_check_in >= 3:
        extra_byte += 10       # 连续签到3天，额外+5byte
        
    user.byte += add_byte + extra_byte
    await user.save()
    
    return {
        'success': True,
        'message': 'success in check in today',
        'data': {
            'add_byte': add_byte,
            'continuous_check_in': user.continuous_check_in,
            'extra_byte': extra_byte
        }
    }
    

async def update_self_info_service(
    user_id: int,
    user_info: UserParams,
) -> None:
    """
    修改个人信息
    
    :param user_id: 玩家id
    :param user_info: 更新后的玩家信息
    
    :return: 修改成功返回 None，否则raise暂时还不知道的错误
    """
    user = await User.filter(id=user_id).select_for_update().first()
    user.name = user_info.name
    user.title = user_info.title

    await user.save()


async def user_upgrade_service():
    pass
    