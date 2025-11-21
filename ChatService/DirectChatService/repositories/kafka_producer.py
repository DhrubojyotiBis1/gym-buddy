from services.kafka.kafka_client import KafkaClient
from repositories.kafka_producer_interface import IKafkaProducer
from config import Config
from logger import get_logger

logger = get_logger()

class KafkaProducer(IKafkaProducer):
    def __init__(self, chat_topic: str = Config.TOPIC_MESSAGES, storage_topic: str = Config.TOPIC_STORAGE):
        self.chat_topic = chat_topic
        self.storage_topic = storage_topic

    async def add_event(self, kafka_client: KafkaClient, data: str, partition: str):
        logger.info("Starting to add event to Kafka. Data: %s, Partition: %s", data, partition)
        await kafka_client.begin_transaction()
        try:
            logger.info("Producing message to chat_topic: %s", self.chat_topic)
            await kafka_client.send(
                topic=self.chat_topic,
                value=data.encode("utf-8"),
                key=partition.encode("utf-8")
            )
            logger.info("Producing message to storage_topic: %s", self.storage_topic)
            await kafka_client.send(
                topic=self.storage_topic,
                value=data.encode("utf-8")
            )
            await kafka_client.commit()
            logger.info("Kafka transaction committed successfully for event.")
        except Exception as e:
            logger.error("Failed to add event to Kafka: %s", str(e))
            # Optionally, handle transaction abort/rollback if your client/provider supports it
            raise
