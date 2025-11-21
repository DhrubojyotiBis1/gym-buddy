from .kafka_connector import KafkaConnector
from logger import get_logger

logger = get_logger()

class KafkaClient:
    def __init__(self, kafka_connector: KafkaConnector):
        # Use the provided kafka_connector instead of always creating a new one
        self.connector = kafka_connector

    async def begin_transaction(self):
        logger.info("Beginning Kafka transaction")
        producer = await self.connector.get_producer()
        await producer.begin_transaction()
        logger.info("Kafka transaction started")
    
    async def commit(self):
        logger.info("Committing Kafka transaction")
        producer = await self.connector.get_producer()
        await producer.commit_transaction()
        logger.info("Kafka transaction committed")

    async def send(self, topic: str, value: bytes, key: bytes = None):
        """
        Send (produce) a message to a Kafka topic.
        """
        logger.info(f"Sending message to Kafka topic '{topic}' with key: {key}")
        producer = await self.connector.get_producer()
        if key is not None:
            await producer.send_and_wait(topic, value=value, key=key)
        else:
            await producer.send_and_wait(topic, value=value)
        logger.info(f"Message sent to Kafka topic '{topic}'")

    async def consume(self, topics, group_id, auto_offset_reset="latest"):
        """
        Create an async iterator (generator) that yields messages from Kafka topics.
        """
        logger.info(f"Consuming topics {topics} with group_id '{group_id}', auto_offset_reset='{auto_offset_reset}'")
        consumer = await self.connector.create_consumer(
            topics=topics if isinstance(topics, (list, tuple)) else [topics],
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
        )
        try:
            async for msg in consumer:
                logger.debug(f"Consumed message from Kafka: {msg}")
                yield msg
        finally:
            logger.info("Stopping Kafka consumer")
            await consumer.stop()

    async def close(self):
        """
        Close underlying Kafka resources, e.g. producer connections.
        """
        logger.info("Closing Kafka connector")
        await self.connector.close()


connector = KafkaConnector()

async def get_kafka_client() -> KafkaClient:
    logger.info("Providing new KafkaClient instance")
    return KafkaClient(connector)

async def close_kafka_connection():
    logger.info("Closing global KafkaConnector")
    await connector.close()