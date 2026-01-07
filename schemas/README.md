# Schemas 模块文档

Schemas 模块使用 Pydantic 定义数据验证模型，用于 API 请求参数验证和响应数据序列化。

## 文件说明

### base_schemas.py

基础模型定义：

```python
class BaseParams(BaseModel):
    """基础参数模型"""
    class Config:
        from_attributes = True  # 允许从 ORM 模型转换
```

### card_schemas.py

卡牌相关模型：

#### UserCardParams（用户卡牌信息）

```python
class UserCardParams(BaseParams):
    card_id: int
    name: str
    image: str
    rarity: int
    package: Package
    unlock_level: int
    description: str
    number: int  # 持有数量
```

#### CardParams（卡牌详情）

```python
class CardParams(BaseParams):
    card_id: int
    name: str
    image: str
    rarity: int
    package: Package
    unlock_level: int
    description: str
    compose_materials: Dict[str, int]  # 合成材料 {卡牌名: 数量}
    decompose_materials: Dict[str, int]  # 分解产物
```

### auth_schemas.py

认证相关模型（当前为预留）。

### record_schemas.py

记录相关模型（当前为预留）。

## 使用示例

### 请求参数验证

```python
from pydantic import Field, validator

class UserParams(BaseParams):
    uid: int = Field(ge=1, title='用户uid')
    name: str = Field(max_length=20, title='用户姓名')
    level: int = Field(default=1, ge=1, title='等级')

    @validator('name')
    def name_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('名称不能包含空格')
        return v
```

### 从 ORM 模型转换

```python
from db.models import Card

card = await Card.get(id=1)
card_param = CardParams.from_orm(card)
# 或 Pydantic v2:
card_param = CardParams.model_validate(card)
```

### 批量转换

```python
cards = await Card.filter(rarity=CardRarity.LEGENDARY).all()
card_params = [CardParams.model_validate(card) for card in cards]
```

### 序列化为 JSON

```python
import json

card_dict = card_param.model_dump()
json_str = json.dumps(card_dict)
```

## Field 参数说明

- `default`: 默认值
- `ge/le`: 大于等于/小于等于
- `gt/lt`: 大于/小于
- `max_length/min_length`: 最大/最小长度
- `regex`: 正则表达式验证
- `title/description`: 字段标题和描述

## 验证器（Validators）

### 字段级验证

```python
from pydantic import field_validator

class CardParams(BaseParams):
    level: int

    @field_validator('level')
    def validate_level(cls, v):
        if v < 1 or v > 100:
            raise ValueError('等级必须在 1-100 之间')
        return v
```

### 模型级验证

```python
from pydantic import model_validator

class OrderParams(BaseParams):
    require_card: List[UserCardParams]
    byte: int
    exp: int

    @model_validator(mode='after')
    def validate_order(self):
        total_cards = sum(c.number for c in self.require_card)
        if total_cards > 10:
            raise ValueError('订单最多包含 10 张卡牌')
        return self
```

## 类型别名与枚举

### 使用枚举类型

```python
from enum import Enum

class CardRarity(str, Enum):
    COMMON = "普通"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"

class CardParams(BaseParams):
    rarity: CardRarity
```

### 类型别名

```python
from typing import Dict, List

CardMaterials = Dict[str, int]  # 卡牌材料类型别名

class CardParams(BaseParams):
    compose_materials: CardMaterials
```

## 响应格式化

### 统一响应格式

```python
class ApiResponse(BaseModel):
    code: int = Field(default=200)
    message: str = Field(default="success")
    data: Any = None

def success_response(data=None):
    return ApiResponse(code=200, message="success", data=data)

def error_response(code, message, data=None):
    return ApiResponse(code=code, message=message, data=data)
```

## 最佳实践

1. **复用模型**: 继承 `BaseParams` 保持一致性
2. **字段验证**: 使用 `Field` 定义约束，避免手动验证
3. **ORM 转换**: 使用 `from_orm()` 或 `model_validate()` 直接从数据库模型转换
4. **JSON 字段**: 对于复杂结构使用 `Dict` 或自定义模型
5. **文档注释**: 为字段添加 `title` 和 `description`，便于生成 API 文档
