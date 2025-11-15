from abc import ABC, abstractmethod

class IKafkaConsumer(ABC):
    @abstractmethod
    async def start_consumer(self):
        """
        Start the Kafka consumer.
        """
        pass
