from abc import ABC, abstractmethod

class IKafkaConnector(ABC):
    @abstractmethod
    async def get_producer(self):
        """
        Returns an initialized Kafka producer instance.
        """
        pass

    @abstractmethod
    async def start_consumer(self, topics, group_id, auto_offset_reset="latest"):
        """
        Initializes and returns a Kafka consumer instance for specified topics and group_id.
        """
        pass

    @abstractmethod
    async def get_consumer(self):
        """
        Returns the singleton Kafka consumer instance if started.
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Closes the producer and consumer connections and cleans up resources.
        """
        pass

