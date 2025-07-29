from grpc_service.exceptions.exception_register import ERROR_MAP
from grpc import StatusCode
from functools import wraps

def http_exception_handler():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, request, context):
            try:
                return await func(self, request, context)
            except Exception as e:
                status = ERROR_MAP.get(e.status_code, StatusCode.INTERNAL)
                await context.abort(status, str(e))
        return wrapper
    return decorator