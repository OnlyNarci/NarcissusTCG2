from pydantic import BaseModel


class BaseParams(BaseModel):
    """基础参数模型"""
    model_config = {
        "extra": "forbid",
        "str_strip_whitespace": True,
    }
    
    def __hash__(self) -> int:
        return hash(self.card_id)
    
    def __getitem__(self, key):
        if key not in self.model_fields:
            raise KeyError(f'{self.__class__.__name__} has no field name {key}')
        raise getattr(self, key)
    
    def __iter__(self):
        return iter(self.model_dump().items())
    