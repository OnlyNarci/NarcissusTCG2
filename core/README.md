# Core 模块文档

Core 模块提供核心配置、中间件、异常处理和工具函数。

## 文件说明

### config.py

应用核心配置，包含：
- 数据库连接配置
- Tortoise-ORM 配置
- 系统参数（服务器端口、超时时间等）

#### Settings 类

```python
class Settings:
    PROJECT_NAME: str = "Narcissus TCG"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "***"
    DB_NAME: str = "narcissus_tcg"
    SESSION_EXPIRE_HOURS = 120
    SERVER_PORT: int = 8000
    SUPER_USER_UID: list[int] = [...]
```

#### Tortoise-ORM 配置

```python
TORTOISE_ORM_CONFIG = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {...}
        }
    },
    'apps': {
        'models': {
            'models': ['db.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
}
```

### middleware.py

NoneBot2 中间件定义：

#### 事件预处理器

- **`temp_utils`**: 处理非命令消息
- **`get_user_id`**: 提取用户信息、验证注册状态、群组权限

#### 运行后处理器

- **`handle_exceptions`**: 统一异常处理，转换为用户友好的错误消息

### exceptions.py

自定义异常类体系：

```python
class ErrorCodes(IntEnum):
    Success = 200
    Unregistered = 402
    Forbidden = 403
    NotFound = 404
    InvalidParams = 422
    InternalServerError = 500

class ClientError(Exception):  # 4xx 错误
    pass

class ServerError(Exception):  # 5xx 错误
    pass

class UnExceptError(Exception):  # 未知错误
    pass

class UnAtomicError(Exception):  # 事务回滚
    pass
```

### ALLOW_GROUPS.json

允许使用机器人功能的 QQ 群列表：

```json
["123456789", "987654321"]
```

## 配置管理

### 修改数据库连接

编辑 `core/config.py` 中的 `Settings` 类：

```python
DB_HOST = "your-host"
DB_PORT = 3306
DB_USER = "your-user"
DB_PASSWORD = "your-password"
DB_NAME = "narcissus_tcg"
```

### 修改超级用户

在 `config.py` 中添加或修改超级用户 QQ 号：

```python
SUPER_USER_UID: list[int] = [1234567890]
```

### 启用群组功能

将群号添加到 `core/ALLOW_GROUPS.json`：

```json
[
    "123456789",
    "987654321"
]
```

## 中间件流程

1. **事件接收** → `temp_utils` 检查是否为临时消息
2. **参数提取** → `get_user_id` 提取用户/群信息到 `state`
3. **命令处理** → endpoints 执行业务逻辑
4. **异常处理** → `handle_exceptions` 捕获异常并发送响应

## 工具函数

### find_project_root

查找项目根目录（定义在 `utils/find_project_root.py`）：

```python
from core.config import project_root
```

## 最佳实践

1. **配置分离**: 服务器基本信息在此配置
2. **异常规范**: 使用标准错误码，便于调试和日志追踪
3. **日志记录**: 在关键操作处添加日志，便于问题排查
