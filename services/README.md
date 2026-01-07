# Services 层开发文档

Services 层是业务逻辑的核心，负责处理具体的业务规则、数据操作和事务管理。

## 目录结构

```
services/
├── __init__.py
├── card_services/      # 卡牌相关服务
├── user_services/      # 用户相关服务
├── store_services/     # 商店相关服务
├── group_services/     # 群组相关服务
└── restaurant_services/  # 餐馆相关服务
```

## 服务规范

### 函数命名

- `query_*`: 查询操作，无副作用
- `create_*`: 创建操作
- `update_*`: 更新操作
- `delete_*`: 删除操作

### 返回值规范

- 查询操作: 返回对象或列表，不存在返回 `None` 或 `[]`
- 创建/更新/删除: 返回操作结果或错误字符串
- 复杂操作: 返回自定义响应模型

## 卡牌服务 (card_services/)

### card_info_services.py

#### 查询卡牌信息

```python
async def query_card_info_service(card_name: str) -> Optional[CardParams]:
    """
    查看指定卡牌的信息

    :param card_name: 卡牌名称
    :return: 卡牌信息模型
    """
    card = await Card.get(name=card_name)
    return CardParams.model_validate(card)
```

#### 查询卡包目录

```python
async def query_package_catalog_service(package: Package) -> List[str]:
    """
    查看指定拓展包的全部可收集卡牌

    :param package: 扩展包名称
    :return: 卡牌名称列表（按稀有度降序）
    """
```

#### 查询合成材料

```python
async def query_card_compose_materials_service(card_id: int) -> List[UserCardParams] | str:
    """
    查看合成一张指定卡牌所需的材料

    :param card_id: 卡牌ID
    :return: 合成所需材料列表
    """
```

## 用户服务 (user_services/)

### user_self_services.py

用户基础操作：注册、签到、等级提升等。

### user_card_services.py

用户卡牌操作：抽卡、合成、分解、查看卡组等。

#### 抽卡示例

```python
async def draw_cards_service(
    user_id: int,
    package: Package,
    num: int
) -> List[CardParams]:
    """
    从指定卡包抽取卡牌

    :param user_id: 用户ID
    :param package: 卡包类型
    :param num: 抽卡数量
    :return: 抽中的卡牌列表
    """
    # 1. 检查用户等级是否满足要求
    # 2. 计算概率并随机抽取卡牌
    # 3. 更新用户卡牌库存
    # 4. 返回抽中卡牌列表
```

### user_order_services.py

订单系统：接收订单、完成订单、过期处理等。

## 商店服务 (store_services/)

### store_card_services.py

商店核心功能：上架、下架、购买卡牌。

#### 上架示例

```python
async def list_card_service(
    user_id: int,
    card_id: int,
    number: int,
    price: int
) -> bool | str:
    """
    上架卡牌到商店

    :param user_id: 用户ID
    :param card_id: 卡牌ID
    :param number: 上架数量
    :param price: 单价
    :return: 成功返回 True，失败返回错误信息
    """
    # 1. 检查用户持有足够数量的卡牌
    # 2. 创建商店记录
    # 3. 扣除用户库存
    # 4. 返回结果
```

### store_record_services.py

交易记录查询。

## 事务处理

### 使用事务装饰器

```python
from tortoise import transactions
from core.exceptions import UnAtomicError

@transactions.atomic()
async def complex_operation(user_id: int, ...):
    # 多个数据库操作
    await User.filter(id=user_id).update(byte=byte - cost)

    # 条件检查
    if some_condition:
        raise UnAtomicError("操作失败，事务回滚")

    await other_operation()
```

### 手动事务控制

```python
from tortoise import transactions

async def manual_transaction():
    conn = transactions.in_transaction()
    await conn.start()
    try:
        # 数据库操作
        await User.create(...)
        await Card.create(...)
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise
```

## 异常处理

### 抛出业务异常

```python
from core.exceptions import ClientError, ServerError

async def some_service(user_id: int):
    user = await User.get(id=user_id)
    if user.byte < 100:
        raise ClientError(
            ErrorCodes.Forbidden,
            message="比特不足",
            required=100,
            current=user.byte
        )
```

### 处理数据库异常

```python
from tortoise.exceptions import DoesNotExist, IntegrityError

async def safe_query(user_id: int):
    try:
        user = await User.get(id=user_id)
        return user
    except DoesNotExist:
        raise ClientError(
            ErrorCodes.NotFound,
            message="用户不存在",
            user_id=user_id
        )
    except IntegrityError as e:
        raise ServerError(
            ErrorCodes.InternalServerError,
            message="数据库错误",
            detail=str(e)
        )
```

## 缓存策略

### 使用内存缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_rarity_probability(rarity: int) -> float:
    """获取稀有度概率（带缓存）"""
    return rarity_probabilities[rarity]
```

### 数据库查询缓存

```python
async def get_card_list_with_cache(package: Package):
    cache_key = f"cards:{package.value}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    cards = await Card.filter(package=package).all()
    await redis_client.setex(cache_key, 3600, json.dumps(cards))
    return cards
```

## 性能优化

### 批量查询

```python
# 避免 N+1 查询
users = await User.all().prefetch_related('cards')

# 使用 values() 减少数据传输
cards = await Card.filter(rarity=CardRarity.LEGENDARY).values('id', 'name')
```

### 批量创建

```python
await Card.bulk_create([
    Card(name="card1", ...),
    Card(name="card2", ...),
])
```

## 最佳实践

1. **单一职责**: 每个服务函数只做一件事
2. **事务一致性**: 涉及多表修改必须使用事务
3. **异常规范**: 使用统一的异常类和错误码
4. **参数验证**: 在 API 层验证，服务层假设参数合法
5. **日志记录**: 关键操作添加日志，便于追踪
6. **性能优先**: 避免循环查询，使用批量操作
