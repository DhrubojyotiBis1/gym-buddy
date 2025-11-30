from services.direct_chat_gprc.stubs import chat_deliver_pb2
from services.direct_chat_gprc.connection_manager_interface import IConnectionManager
from logger import get_logger

logger = get_logger()

class DirectChatClient:
    @staticmethod
    async def send_message(connection_manager: IConnectionManager, message: str, host: str, port: str, 
    receiver_email: str, sender_email: str):
        """
        Sends a direct chat message via gRPC.

        Args:
            connector (DirectChatClientConnector): Established connector with a stub.
            message (str): The chat message content.
            service (str): The destination service identifier.
            sender_email (str): The sender's email.

        Returns:
            gRPC response object
        """
        logger.debug(
            f"Preparing to send message via gRPC. message='{message}', sender_email='{sender_email}', receiver_email='{receiver_email}', host='{host}', port='{port}'"
        )
        request = chat_deliver_pb2.DirectChatMessageRequest(
            message=message,
            sender_email=sender_email,
            receiver_email=receiver_email
        )
        connector = await connection_manager.get_connector(host, port)
        logger.info(
            f"Sending gRPC message from '{sender_email}' to '{receiver_email}' via {host}:{port}."
        )
        response = await connector.stub.SendMessage(request)
        logger.info(
            f"gRPC message sent from '{sender_email}' to '{receiver_email}' via {host}:{port} (response: {response!r})"
        )
        return response
