import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from config import Config
from starlette.exceptions import HTTPException as StarletteHTTPException

class JWT():
    def __init__(self, path=Config.PRIVATE_KEY_PATH):
        self.private_key = self._load_private_key(path)
        self.public_key = self.private_key.public_key()

    def _load_private_key(self, file_path):
        with open(file_path, 'rb') as f:
            return serialization.load_pem_private_key(f.read(), password=None)

    def _generate_token(self, user_info, type: str, time: timedelta, algorithm: str = Config.JWT_ALGORITHM) :
        payload = {"user": user_info, "exp": datetime.now()+time, "type": type}
        token = jwt.encode(payload, self.private_key, algorithm=algorithm)
        return token
    
    def _decode_token(self, token: str, algorithm: str = Config.JWT_ALGORITHM):
        user_info = jwt.decode(token, self.public_key, algorithms=[algorithm])
        return user_info

    def create_new_tokens(self, user_info):
        access_token = self._generate_token(user_info, Config.JWT_ACCESS_TOKEN_TYPE, timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXP_TIME_IN_MINUTS))
        refresh_token = self._generate_token(user_info, Config.JWT_REFRESH_TOKEN_TYPE, timedelta(minutes=Config.JWT_REFRESH_TOKEN_EXP_TIME_IN_MINUTS))
        #TODO: Insert the refresh token in redis
        return {"access_token": access_token, "refresh_token": refresh_token}
    
    def refresh_token(self, refresh_token: str):
        #TODO: check if token exist in redis
        user_info = self._decode_token(refresh_token)
        if "type" not in user_info or user_info["type"] != Config.JWT_REFRESH_TOKEN_TYPE:
            raise StarletteHTTPException(400, 'Invalid Refresh Token')
        #TODO: delete existing refresh token from redis
        return self.create_new_tokens(user_info)