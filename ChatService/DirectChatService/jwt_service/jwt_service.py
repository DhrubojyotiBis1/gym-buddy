import logging
from fastapi import status, WebSocket, WebSocketDisconnect
from cryptography.hazmat.primitives import serialization
from config import Config
import aiofiles
import jwt
from logger import get_logger

logger = get_logger()

async def _get_public_key():
    logger.info(f"Loading public key from: {Config.PUBLIC_KEY_PATH}")
    async with aiofiles.open(Config.PUBLIC_KEY_PATH, 'rb') as f:
        data = await f.read()
    logger.debug("Public key loaded, deserializing...")
    return serialization.load_pem_public_key(data)

#TODO: Create WS exception handler 
async def verify_jwt(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        logger.warning("Token missing")
        # Add reason as close reason when disconnecting
        raise WebSocketDisconnect(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Token missing in WebSocket query parameters"
        )

    try:
        public_key = await _get_public_key()
        decoded = jwt.decode(token, public_key, algorithms=[Config.JWT_ALGORITHM])
        return decoded.get("user")

    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT")
        raise WebSocketDisconnect(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="JWT token expired"
        )

    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT")
        raise WebSocketDisconnect(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid JWT token"
        )

    except Exception as ex:
        logger.error(f"Unexpected JWT error: {ex}")
        raise WebSocketDisconnect(
            code=status.WS_1011_INTERNAL_ERROR,
            reason=f"Unexpected JWT error: {ex}"
        )
