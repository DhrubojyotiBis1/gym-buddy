
import grpc
from services.grpc.stubs import chat_deliver_pb2_grpc, chat_deliver_pb2
from logger import get_logger
from services.websocket.manager import WebsocketConnectionManager

logger = get_logger()
manager = WebsocketConnectionManager()

class MessageDeliveryService(chat_deliver_pb2_grpc.DirectChatServicer):
    async def SendMessage(self, request, context):
        sender = request.sender_email
        receiver = request.receiver_email
        message = request.message
        logger.info(f"Received SendMessage RPC. Sender: {sender}, Receiver: {receiver}, Message: {message}")

        #TODO: Format the message using formater module

        try:
            await manager.send_message_to_user(message=message, user_id=receiver)
            response_message = f"Message delivered from {sender} to {receiver}"
            logger.info(f"Message successfully delivered to {receiver} from {sender}")
            return chat_deliver_pb2.Response(message=response_message)
        except Exception as e:
            error_msg = f"Failed to deliver message from {sender} to {receiver}: {str(e)}"
            logger.error(error_msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(error_msg)
            return chat_deliver_pb2.Response(message=error_msg)

