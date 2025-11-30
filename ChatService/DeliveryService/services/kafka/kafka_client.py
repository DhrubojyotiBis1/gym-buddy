from .kafka_connector_interface import IKafkaConnector
from logger import get_logger

logger = get_logger()

class KafkaClient:
    @staticmethod
    async def begin_transaction(connector: IKafkaConnector):
        logger.info("Beginning Kafka transaction")
        producer = await connector.get_producer()
        await producer.begin_transaction()
        logger.info("Kafka transaction started")

    @staticmethod
    async def commit(connector: IKafkaConnector):
        logger.info("Committing Kafka transaction")
        producer = await connector.get_producer()
        await producer.commit_transaction()
        logger.info("Kafka transaction committed")

    @staticmethod
    async def send(topic: str, value: bytes, connector: IKafkaConnector, key: bytes = None):
        """
        Send (produce) a message to a Kafka topic.
        """
        logger.info(f"Sending message to Kafka topic '{topic}' with key: {key}")
        producer = await connector.get_producer()
        if key is not None:
            await producer.send_and_wait(topic, value=value, key=key)
        else:
            await producer.send_and_wait(topic, value=value)
        logger.info(f"Message sent to Kafka topic '{topic}'")

    @staticmethod
    async def consume(topics, group_id, connector: IKafkaConnector, auto_offset_reset="latest"):
        """
        Create an async iterator (generator) that yields messages from Kafka topics.
        """
        logger.info(f"Consuming topics {topics} with group_id '{group_id}', auto_offset_reset='{auto_offset_reset}'")
        await connector.start_consumer(topics, group_id, auto_offset_reset=auto_offset_reset)
        consumer = await connector.get_consumer()
        try:
            async for msg in consumer:
                logger.debug(f"Consumed message from Kafka: {msg}")
                yield msg
        finally:
            logger.info("Stopping Kafka consumer")
            await consumer.stop()

    @staticmethod
    async def close(connector: IKafkaConnector):
        """
        Close underlying Kafka resources, e.g. producer connections.
        """
        logger.info("Closing Kafka connector")
        await connector.close()