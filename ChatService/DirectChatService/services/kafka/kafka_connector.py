from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
from config import Config
from logger import get_logger

logger = get_logger()

class KafkaConnector:
    def __init__(self, bootstrap_servers: str = Config.KAFKA_BOOTSTRAP_SERVERS, 
    client_id: str = Config.KAFKA_CLIENT_ID, transactional_id: str = Config.KAFKA_TRANSACTION_ID):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self._producer = None
        self._producer_lock = asyncio.Lock()
        self.transactional_id = transactional_id

    async def get_producer(self):
        async with self._producer_lock:
            if self._producer is None:
                logger.info("Initializing new AIOKafkaProducer with bootstrap_servers=%s, client_id=%s, transactional_id=%s",
                            self.bootstrap_servers, self.client_id, self.transactional_id)
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    transactional_id=self.transactional_id,
                    client_id=self.client_id,
                )
                await self._producer.start()
                logger.info("AIOKafkaProducer started successfully")
            else:
                logger.debug("AIOKafkaProducer already initialized, returning existing producer")
            return self._producer

    async def create_consumer(self, topics, group_id, auto_offset_reset="latest"):
        logger.info("Creating new AIOKafkaConsumer for topics=%s, group_id=%s, auto_offset_reset=%s",
                    topics, group_id, auto_offset_reset)
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
        )
        await consumer.start()
        logger.info("AIOKafkaConsumer started successfully for topics=%s, group_id=%s", topics, group_id)
        return consumer

    async def close(self):
        async with self._producer_lock:
            if self._producer:
                logger.info("Stopping AIOKafkaProducer...")
                await self._producer.stop()
                self._producer = None
                logger.info("AIOKafkaProducer stopped and cleaned up")
