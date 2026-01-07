# Database 层开发文档

DB 层负责数据模型定义、数据库连接和依赖管理。

## 文件说明

### models.py

所有数据模型定义，基于 Tortoise-ORM。

### model_dependencies.py

数据依赖项定义（枚举类型、常量等）。

## 数据模型

### User（用户表）

```python
class User(Model):
    id = fields.IntField(pk=True)
    uid = fields.CharField(unique=True)  # QQ 号
    name = fields.CharField(max_length=20)  # 用户名
    title = fields.CharField(default='萌新')  # 称号
    level = fields.IntField(default=1)  # 等级
    exp = fields.IntField(default=0)  # 经验值
    byte = fields.IntField(default=0)  # 比特（货币）
    last_check_in = fields.DateField()  # 最后签到日期
    continuous_check_in = fields.IntField()  # 连续签到天数
    created_at = fields.DatetimeField(auto_now_add=True)
    cards = fields.ManyToManyField('models.Card', through='user_card')
```

### Card（卡牌表）

```python
class Card(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(unique=True)
    image = fields.CharField()  # 卡图 URL
    rarity = fields.IntEnumField(CardRarity)  # 稀有度
    package = fields.CharEnumField(Package)  # 所属卡包
    unlock_level = fields.IntField()  # 解锁等级
    description = fields.CharField()
    compose_materials = fields.JSONField()  # 合成材料
    decompose_materials = fields.JSONField()  # 分解产物
    created_at = fields.DatetimeField(auto_now_add=True)
```

### UserCard（用户-卡牌关系表）

```python
class UserCard(Model):
    user = fields.ForeignKeyField('models.User')
    card = fields.ForeignKeyField('models.Card')
    number = fields.IntField(default=1)  # 持有数量
    class Meta:
        unique_together = (('user', 'card'),)
```

### Store（商店表）

```python
class Store(Model):
    card = fields.ForeignKeyField('models.Card')
    owner = fields.ForeignKeyField('models.User')
    number = fields.IntField()  # 上架数量
    price = fields.IntField()  # 单价
    class Meta:
        unique_together = (('card', 'owner'),)
```

### StoreRecord（交易记录表）

```python
class StoreRecord(Model):
    buyer = fields.ForeignKeyField('models.User')
    seller = fields.ForeignKeyField('models.User')
    card = fields.ForeignKeyField('models.Card')
    number = fields.IntField()
    price = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
```

### Group（群组表）

```python
class Group(Model):
    uid = fields.CharField(unique=True)  # 群号
    name = fields.CharField(max_length=16)  # 群名
    owner = fields.ForeignKeyField('models.User', null=True)
    level = fields.IntField(default=1)  # 群等级
    created_at = fields.DatetimeField(auto_now_add=True)
```

### GroupUser（群组-用户关系表）

```python
class GroupUser(Model):
    group = fields.ForeignKeyField('models.Group')
    user = fields.ForeignKeyField('models.User')
    status = fields.IntEnumField(GroupMemberStatus)  # 成员状态
    level = fields.IntField()  # 群内等级
    title = fields.CharField(max_length=16)  # 群称号
    class Meta:
        unique_together = (('group', 'user'),)
```

### Order（订单表）

```python
class Order(Model):
    user = fields.ForeignKeyField('models.User')
    require_card = fields.JSONField()  # 所需卡牌
    byte = fields.IntField()  # 奖励比特
    exp = fields.IntField()  # 奖励经验
    status = fields.IntEnumField(OrderStatus)  # 订单状态
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField()  # 过期时间
```

### Restaurant（餐馆表）

```python
class Restaurant(Model):
    user = fields.ForeignKeyField('models.User', unique=True)
    main_business = fields.CharEnumField(RestaurantBusiness)
    last_change_business = fields.DateField()
    city = fields.CharEnumField(City)
    created_at = fields.DatetimeField(auto_now_add=True)
```

### UserTask（任务表）

```python
class UserTask(Model):
    user = fields.ForeignKeyField('models.User')
    status = fields.IntEnumField(TaskStatus)
```

## 枚举类型定义

### CardRarity（卡牌稀有度）

```python
class CardRarity(IntEnum):
    COMMON = 1    # 普通
    RARE = 2      # 稀有
    EPIC = 3      # 史诗
    LEGENDARY = 4 # 传说
    SP = 5        # SP
```

### Package（卡牌包）

```python
class Package(str, Enum):
    BASE = "base"           # 基础包
    LIGHTING_HARBOR = "lighting_harbor"  # 光明港
    STAR_VALLEY = "star_valley"          # 星光谷
    ...
```

### GroupMemberStatus（群成员状态）

```python
class GroupMemberStatus(IntEnum):
    BLACKLIST = 0  # 黑名单
    PENDING = 1    # 申请中
    MEMBER = 2     # 普通成员
    ADMIN = 3      # 管理员
    OWNER = 4      # 群主
```

### OrderStatus（订单状态）

```python
class OrderStatus(IntEnum):
    WAITING = 0      # 待完成
    COMPLETED = 1    # 已完成
    TIMEOUT = 2      # 超时
    REJECTED = 3     # 已拒绝
```

### TaskStatus（任务状态）

```python
class TaskStatus(IntEnum):
    WAITING = 0      # 待完成
    COMPLETED = 1    # 已完成
```

## 数据库操作

### 查询示例

```python
# 单条查询
user = await User.get(id=user_id)

# 条件查询
cards = await Card.filter(rarity=CardRarity.LEGENDARY).all()

# 关联查询
user_cards = await user.cards.all().prefetch_related('card')

# JSON 字段查询
cards = await Card.filter(compose_materials__contains=str(card_id)).all()
```

### 创建/更新示例

```python
# 创建
new_user = await User.create(uid="123456", name="玩家1")

# 更新
await user.filter(id=user_id).update(level=2)

# 关联操作
await user.cards.add(card)
await user.cards.remove(card)
```

### 事务处理

```python
from tortoise import transactions

@transactions.atomic()
async def transfer_card(from_user, to_user, card_id):
    # 原子操作，失败自动回滚
    await from_user.cards.remove(card_id)
    await to_user.cards.add(card_id)
```

## 数据库迁移

### Aerich 使用

```bash
# 初始化
aerich init -t core.config.TORTOISE_ORM_CONFIG

# 创建迁移
aerich migrate --name "add_new_field"

# 应用迁移
aerich upgrade

# 回滚
aerich downgrade
```

## 索引优化

模型已定义以下索引：

- `Card`: (package), (rarity, package), (name, rarity, package)
- `Store`: (card, price)
- `StoreRecord`: (buyer, created_at), (seller, created_at)
- `GroupUser`: (group, user, status)

## 最佳实践

1. **使用 `prefetch_related`**: 关联查询时预加载，避免 N+1 问题
2. **JSON 字段**: 用于存储复杂结构（如合成材料），但不建议用于频繁查询
3. **事务控制**: 涉及多表修改时使用 `@transactions.atomic()`
4. **唯一约束**: 多字段唯一约束使用 `unique_together`
