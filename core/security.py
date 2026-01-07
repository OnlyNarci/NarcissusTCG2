from tortoise.exceptions import DoesNotExist
from db.models import User
from core.exceptions import ErrorCodes, ClientError


async def get_current_user_id(uid: str) -> int:
    """
    从 request.state 中获取当前用户的 ID。
    如果不存在，则抛出 Unauthorized 异常。
    """
    try:
        user = await User.get(uid=uid)
    except DoesNotExist:
        raise ClientError(error_code=ErrorCodes.Unregistered, message='登录已过期，请重新登录')
    return user.id

