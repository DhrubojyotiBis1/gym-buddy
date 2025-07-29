from grpc_service.exceptions.exceptions import *
from grpc import StatusCode

#TODO: create an actual register with decorator
ERROR_MAP = {
    404: StatusCode.NOT_FOUND,
    401: StatusCode.UNAUTHENTICATED,
    500: StatusCode.INVALID_ARGUMENT
}