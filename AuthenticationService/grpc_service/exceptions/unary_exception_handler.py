from grpc.aio import UnaryUnaryClientInterceptor
from grpc import StatusCode
from starlette.exceptions import HTTPException as StarletteHTTPException
import grpc

GRPC_TO_HTTP_STATUS = {
    StatusCode.NOT_FOUND: 404,
    StatusCode.UNAUTHENTICATED: 401,
    StatusCode.PERMISSION_DENIED: 403,
    StatusCode.INVALID_ARGUMENT: 400,
    StatusCode.INTERNAL: 500,
}

class HttpExceptionHandlingInterceptor(UnaryUnaryClientInterceptor):
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        try:
            return await continuation(client_call_details, request)
        except grpc.aio.AioRpcError as e:
            status_code = GRPC_TO_HTTP_STATUS.get(e.code(), 500)
            raise StarletteHTTPException(status_code=status_code, detail=e.details() or "gRPC error")
