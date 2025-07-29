from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UserCheck(_message.Message):
    __slots__ = ("email", "hashed_password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    HASHED_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    hashed_password: str
    def __init__(self, email: _Optional[str] = ..., hashed_password: _Optional[str] = ...) -> None: ...

class UserCreate(_message.Message):
    __slots__ = ("name", "email", "hashed_password")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    HASHED_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    hashed_password: str
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ..., hashed_password: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...
