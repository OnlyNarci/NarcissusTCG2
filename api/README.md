# API 层开发文档

API 层负责接收用户请求、参数验证、调用 Services 层处理业务逻辑，并返回响应结果。

## 目录结构

```
api/
├── __init__.py
├── dependencies/      # 依赖注入和路由配置
└── endpoints/         # 命令端点
    ├── user_endpoints/    # 用户相关命令
    ├── card_endpoints/    # 卡牌相关命令
    ├── store_endpoints/   # 商店相关命令
    └── plugins/           # 插件端点
```

## 命令端点规范

### 命令注册

使用 NoneBot2 的 `on_command()` 或 Alconna 的 `MatchEntry()` 装饰器：

```python
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

# 方式 1: 使用 on_command
register_cmd = on_command("注册")

@register_cmd.handle()
async def handle_register(event: GroupMessageEvent, state: T_State):
    user_id = state['user_id']
    # 业务逻辑...

# 方式 2: 使用 Alconna（推荐用于复杂命令）
from nonebot_plugin_alconna import MatchEntry, on_alconna

# 在插件 __init__.py 中配置
_alc = Alconna("抽卡", Args["num", int])
matcher = on_alconna(_alc)
```

### 参数获取

从 `state` 对象中获取预处理后的参数：

- `state['user_uid']`: 用户 QQ 号
- `state['user_id']`: 用户数据库 ID
- `state['group_id']`: 群号（仅群聊消息）
- `state['user_name']`: 用户昵称

### 游客路由

某些功能允许未注册用户使用，需要在 `api/dependencies/routes.py` 中添加：

```python
tourist_routes = ['注册', '帮助', ...]
```

## 端点分类

### 用户端点 (`user_endpoints/`)

用户账号相关命令：
- 注册/登录
- 个人信息查询
- 每日签到
- 订单管理

### 卡牌端点 (`card_endpoints/`)

卡牌相关命令：
- 抽卡
- 卡牌查询
- 卡牌合成/分解
- 卡图展示

### 商店端点 (`store_endpoints/`)

商店交易相关命令：
- 上架/下架
- 购买卡牌
- 交易记录查询

## 中间件集成

API 层依赖以下中间件（定义在 `core/middleware.py`）：

1. **`temp_utils`**: 临时消息处理（非命令消息）
2. **`get_user_id`**: 提取用户信息并注册到 `state`
3. **`handle_exceptions`**: 统一异常处理

## 异常抛出

使用自定义异常类：

```python
from core.exceptions import ClientError

# 抛出客户端错误
raise ClientError(
    ErrorCodes.InvalidParams,
    message="参数错误",
    param_name="card_name"
)
```

## 最佳实践

1. **参数验证**: 使用 `state` 中的预处理数据，避免重复解析消息
2. **错误处理**: 抛出具体的异常类型，由中间件统一处理响应
3. **业务分离**: 只负责请求/响应处理，业务逻辑放在 Services 层
4. **日志记录**: 使用 `log/log_config/service_logger` 记录关键操作
