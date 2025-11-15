from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from jwt_service.jwt_service import verify_jwt
from services.direct_chat_service import DirectChatService
from connection_services.websocket.manager import WebsocketConnectionManager

router = APIRouter(
    prefix="/direct-chat",
    tags=["Direct Chat"]
)

direct_chat_service = DirectChatService(WebsocketConnectionManager())

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, user = Depends(verify_jwt) ):
    await direct_chat_service.add_connection(user, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await direct_chat_service.send_message(data, user)
    except WebSocketDisconnect:
        direct_chat_service.disconnect(user, websocket)

