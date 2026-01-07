# NarcissusTCG 开发者文档

基于 NoneBot2 框架开发的 TCG（集换式卡牌游戏）QQ 机器人，支持用户抽卡、卡牌合成/分解、玩家交易、任务订单等核心玩法。

## 项目概述

- **技术栈**: Python 3.10+、NoneBot2、FastAPI、Tortoise-ORM、MySQL
- **架构模式**: 分层架构（API 层 → Services 层 → DB 层）
- **异步驱动**: 全异步设计，基于 asyncio 和 Tortoise-ORM

## 快速开始

### 环境要求

- Python 3.10 或更高版本
- MySQL 8.0+
- OneBot V11 协议的 QQ 客户端（如 NapCat、Lagrange 等）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd NarcissusTCG
   ```

2. **安装依赖**
   ```bash
   pip install -r pyproject.toml
   ```

3. **配置数据库**
   - 创建 MySQL 数据库 `narcissus_tcg`
   - 修改 `core/config.py` 中的数据库连接信息
   - 执行数据库迁移：
     ```bash
     aerich init -t core.config.TORTOISE_ORM_CONFIG
     aerich upgrade
     ```

4. **配置机器人**
   - 修改 `config.py` 中的 WebSocket 连接地址
   - 修改 `core/ALLOW_GROUPS.json` 配置允许的 QQ 群

5. **启动服务**
   ```bash
   python bot.py
   ```

## 项目结构

```
NarcissusTCG/
├── api/                # API 路由层，处理用户命令和请求
├── core/              # 核心配置和中间件
├── db/                # 数据模型和数据库配置
├── schemas/           # Pydantic 数据验证模型
├── services/          # 业务逻辑层
├── utils/             # 工具函数
├── log/               # 日志配置
├── static/            # 静态资源
└── tests/             # 测试文件
```

## 目录文档

各模块详细文档请参考：
- [api/](api/README.md) - API 层详细说明
- [core/](core/README.md) - 核心模块文档
- [db/](db/README.md) - 数据模型文档
- [schemas/](schemas/README.md) - 数据模型文档
- [services/](services/README.md) - 业务服务文档

## 开发指南

### 添加新命令

1. 在 `api/endpoints/` 对应目录下创建命令处理函数
2. 在 `services/` 对应目录下编写业务逻辑
3. 使用 `@on_command()` 或 `@MatchEntry()` 装饰器注册命令

### 数据库迁移

```bash
# 创建新迁移
aerich migrate

# 应用迁移
aerich upgrade

# 查看迁移历史
aerich history
```

### 异常处理

- `ClientError`: 客户端错误（4xx）
- `ServerError`: 服务器错误（5xx）
- `UnExceptError`: 未知错误
- `UnAtomicError`: 事务回滚

详见 `core/exceptions.py`

## 许可证

参见 LICENSE 文件
