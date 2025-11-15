from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

class KafkaConnector:
    def __init__(self, bootstrap_servers=None, client_id=None):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self._producer = None

    async def get_producer(self):
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
            )
            await self._producer.start()
        return self._producer

    async def create_consumer(self, topics, group_id, auto_offset_reset="latest"):
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
        )
        await consumer.start()
        return consumer

    async def close(self):
        if self._producer:
            await self._producer.stop()
