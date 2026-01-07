from enum import IntEnum
from typing import Any


class ErrorCodes(IntEnum):
    EarlyHints = 103
    Success = 200       # 请求成功
    Accept = 202        # 收到请求
    NoContent = 203     # 无请求内容
    BadRequest = 400
    Unregistered = 402      # 用户未注册
    Forbidden = 403
    NotFound = 404
    RequestTimeout = 408
    Conflict = 409
    PayloadTooLarge = 413
    InvalidParams = 422     # 参数校验未通过（不合法参数）
    InternalServerError = 500   # 服务器错误
    UnExceptError = 1000


class ClientError(Exception):
    """客户端错误，4头错误码"""
    def __init__(self, error_code: ErrorCodes, message: str = "", **kwargs: Any):
        self.error_code: int = error_code
        self.status_code: int = error_code.value
        self.message = message
        self.data = kwargs
        super().__init__(f"[{error_code.value}] {message or error_code.name}")


class ServerError(Exception):
    """服务端错误，5头错误码"""
    def __init__(self, error_code: ErrorCodes, message: str = "", **kwargs: Any):
        self.error_code: int = error_code
        self.status_code: int = error_code.value
        self.message = message
        self.data = kwargs
        super().__init__(f"[{error_code.value}] {message or error_code.name}")


class UnExceptError(Exception):
    """未知错误，错误码1000"""
    def __init__(self, message: str = "", **kwargs: Any):
        self.error_code = ErrorCodes.UnExceptError
        self.status_code = 1000
        self.message = message
        self.data = kwargs
        super().__init__(f"[1000] {message}")


class UnAtomicError(Exception):
    """用于在一个原子事务内部中断，使事务回滚"""
    def __init__(self, message: str = "", **kwargs: Any):
        super().__init__(message)
        self.message = message
        self.data = kwargs
        