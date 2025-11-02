from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException 
from cryptography.hazmat.primitives import serialization
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from config import Config
import aiofiles
import jwt

_security = HTTPBearer()

async def _get_public_key():
    async with aiofiles.open(Config.PUBLIC_KEY_PATH, 'rb') as f:
        data = await f.read()
    return serialization.load_pem_public_key(data)


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(_security), 
                     public_key = Depends(_get_public_key)):
    token = credentials.credentials
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=[Config.JWT_ALGORITHM])
        return decoded_token['user']
    except jwt.ExpiredSignatureError:
        raise StarletteHTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise StarletteHTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise StarletteHTTPException(status_code=500, detail='JWT decoding failed')