from pydantic import Field
from schemas import BaseParams


class UserParams(BaseParams):
    """用户模型"""
    name: str = Field(min_length=0, max_length=20, title='玩家qq昵称')
    uid: int = Field(ge=1, title='玩家qq号')
    