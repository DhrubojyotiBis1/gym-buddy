from repositories.kafka_consumer_interface import IKafkaConsumer
from connection_services.kafka.kafka_client import KafkaClient

class KafkaConsumer(IKafkaConsumer):
    def __init__(self, kafka_client: KafkaClient, topics, group_id, auto_offset_reset="latest"):
        self.kafka_client = kafka_client
        self.topics = topics
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset

    async def start_consumer(self):
        """
        Start the Kafka consumer and yield messages.
        """
        async for msg in self.kafka_client.consume(
            topics=self.topics,
            group_id=self.group_id,
            auto_offset_reset=self.auto_offset_reset
        ):
            yield msg

