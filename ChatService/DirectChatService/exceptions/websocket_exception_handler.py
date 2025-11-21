import logging
from fastapi import WebSocketDisconnect
from fastapi.responses import Response
from logger import get_logger

logger = get_logger()

#TODO: Raise appropriate Http exception
def register_exception_handlers(app):
    @app.exception_handler(WebSocketDisconnect)
    async def websocket_disconnect_handler(request, exc):
        logger.warning(f"WS disconnected: code={getattr(exc, 'code', '')} reason={getattr(exc, 'reason', '')}")
        return Response(status_code=400)
