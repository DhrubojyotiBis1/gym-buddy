from abc import ABC, abstractmethod

class IKafkaProducer(ABC):
    @abstractmethod
    async def add_event(self, data: str):
        """
        Add an event to the Kafka producer.
        """
        pass
