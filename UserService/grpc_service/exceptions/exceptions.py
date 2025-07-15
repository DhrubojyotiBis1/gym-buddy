from grpc import StatusCode

#TODO: Implement proper Exeception classes 
class GRPCError(Exception):
    status_code = StatusCode.INTERNAL
    default_message = "Internal server error"

    def __init__(self, message=None):
        super().__init__(message or self.default_message)

class NotFoundError(GRPCError):
    status_code = StatusCode.NOT_FOUND
    default_message = "Resource not found"


class UnauthorizedError(GRPCError):
    status_code = StatusCode.UNAUTHENTICATED
    default_message = "Unauthorized access"


class InvalidInputError(GRPCError):
    status_code = StatusCode.INVALID_ARGUMENT
    default_message = "Invalid input"