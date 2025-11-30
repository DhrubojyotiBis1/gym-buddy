from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from services.kafka.kafka_connector_interface import IKafkaConnector
import asyncio
from config import Config
from logger import get_logger

logger = get_logger()

class KafkaConnector(IKafkaConnector):
    def __init__(self, 
                 bootstrap_servers: str = Config.KAFKA_BOOTSTRAP_SERVERS, 
                 client_id: str = Config.KAFKA_CLIENT_ID, 
                 transactional_id: str = Config.KAFKA_TRANSACTIONAL_ID):
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self._producer = None
        self._producer_lock = asyncio.Lock()
        self.transactional_id = transactional_id

        self._consumer = None
        self._consumer_lock = asyncio.Lock()
        self._consumer_offset_reset = None

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

    async def start_consumer(self, topics, group_id, auto_offset_reset="latest"):
        """
        Initialize (or reinitialize) a singleton consumer with the provided topics and group_id.
        Can only be called once per service lifetime.
        """
        async with self._consumer_lock:
            if self._consumer is not None:
                logger.info(
                    "AIOKafkaConsumer already initialized with topics=%s, group_id=%s. Returning existing consumer.",
                    self._consumer_topics, self._consumer_group_id
                )
                return self._consumer
            if not topics or not group_id:
                raise ValueError("Consumer topics and group_id must be provided to start_consumer")
            self._consumer_topics = topics
            self._consumer_group_id = group_id
            logger.info(
                "Creating new AIOKafkaConsumer for topics=%s, group_id=%s, auto_offset_reset=%s",
                topics, group_id, auto_offset_reset
            )
            self._consumer = AIOKafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
            )
            await self._consumer.start()
            logger.info(
                "AIOKafkaConsumer started successfully for topics=%s, group_id=%s",
                topics, group_id
            )
            self._consumer_offset_reset = auto_offset_reset
            return self._consumer

    async def get_consumer(self):
        """
        Returns the singleton Kafka consumer instance if started.
        """
        async with self._consumer_lock:
            if self._consumer is None:
                raise RuntimeError("Kafka consumer has not been created. Call start_consumer first.")
            return self._consumer

    async def close(self):
        async with self._producer_lock:
            if self._producer:
                logger.info("Stopping AIOKafkaProducer...")
                await self._producer.stop()
                self._producer = None
                logger.info("AIOKafkaProducer stopped and cleaned up")
        async with self._consumer_lock:
            if self._consumer:
                logger.info("Stopping AIOKafkaConsumer...")
                await self._consumer.stop()
                self._consumer = None
                logger.info("AIOKafkaConsumer stopped and cleaned up")
