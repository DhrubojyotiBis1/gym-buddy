import asyncio

from services.delivery import DeliveryService
from services.kafka.kafka_connector import KafkaConnector
from repositories.redis_repository import RedisRepository
from services.direct_chat_gprc.connection_manager import DirectChatConnectionManager
from services.redis.redis_connector import RedisConnector

async def main():
    kafka_connector = KafkaConnector()
    redis_repository = RedisRepository()
    connection_manager = DirectChatConnectionManager()
    redis_connector = RedisConnector()

    delivery_service = DeliveryService(
        kafka_connector=kafka_connector,
        redis=redis_repository,
        connection_manager=connection_manager
    )
    await delivery_service.start(redis_connector)


if __name__ == "__main__":
    asyncio.run(main())
