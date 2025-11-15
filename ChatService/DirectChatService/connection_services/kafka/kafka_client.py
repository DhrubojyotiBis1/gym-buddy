from .kafka_connector import KafkaConnector
import asyncio

class KafkaClient:
    def __init__(self, kafka_connector: KafkaConnector):
        # Use the provided kafka_connector instead of always creating a new one
        self.connector = kafka_connector

    async def begin_transaction(self):
        producer = await self.connector.get_producer()
        await producer.begin_transaction()
    
    async def commit(self):
        producer = await self.connector.get_producer()
        await producer.commit_transaction()

    async def send(self, topic: str, value: bytes, key: bytes = None):
        """
        Send (produce) a message to a Kafka topic.
        """
        producer = await self.connector.get_producer()
        if key is not None:
            await producer.send_and_wait(topic, value=value, key=key)
        else:
            await producer.send_and_wait(topic, value=value)

    async def consume(self, topics, group_id, auto_offset_reset="latest"):
        """
        Create an async iterator (generator) that yields messages from Kafka topics.
        """
        consumer = await self.connector.create_consumer(
            topics=topics if isinstance(topics, (list, tuple)) else [topics],
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
        )
        try:
            async for msg in consumer:
                yield msg
        finally:
            await consumer.stop()

    async def close(self):
        """
        Close underlying Kafka resources, e.g. producer connections.
        """
        await self.connector.close()
