from connection_services.kafka.kafka_client import KafkaClient
from repositories.kafka_producer_interface import IKafkaProducer

class KafkaProducer(IKafkaProducer):
    def __init__(self, kafka_client: KafkaClient, chat_topic: str, storage_topic: str):
        self.kafka_client = kafka_client
        self.chat_topic = chat_topic
        self.storage_topic = storage_topic

    async def add_event(self, data: str, partition: str):
        # Begin Kafka transaction
        await self.kafka_client.begin_transaction()
        try:
            # Produce message to chat_topic with partition
            await self.kafka_client.send(
                topic=self.chat_topic,
                value=data.encode("utf-8"),
                key=partition
            )
            # Produce message to storage_topic
            await self.kafka_client.send(
                topic=self.storage_topic,
                value=data.encode("utf-8")
            )
            # Commit transaction
            await self.kafka_client.commit()
        except Exception:
            # Optionally, handle transaction abort/rollback if your client/provider supports it
            raise
