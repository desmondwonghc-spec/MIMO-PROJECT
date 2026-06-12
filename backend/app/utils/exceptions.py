"""
自定义异常和错误处理
"""
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """应用自定义异常基类"""
    def __init__(self, detail: str, error_code: str, status_code: int = 400):
        self.detail = detail
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppError):
    """资源未找到"""
    def __init__(self, resource: str, resource_id: str = ""):
        detail = f"{resource}未找到"
        if resource_id:
            detail = f"{resource} '{resource_id}' 未找到"
        super().__init__(detail=detail, error_code=f"{resource.upper()}_NOT_FOUND", status_code=404)


class ValidationError(AppError):
    """数据验证错误"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, error_code="VALIDATION_ERROR", status_code=422)


class AIError(AppError):
    """AI 服务调用错误"""
    def __init__(self, detail: str):
        super().__init__(detail=detail, error_code="AI_SERVICE_ERROR", status_code=502)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """自定义异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code},
    )
