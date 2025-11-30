from redis.asyncio.connection import ConnectionPool
from services.redis.redis_connector_interface import IRedisConnector
from config import Config

class RedisConnector(IRedisConnector):
    def __init__(self, host: str = Config.REDIS_HOSTNAME, port: int = Config.REDIS_PORT, 
                 db: int = Config.REDIS_DB, max_connections: int = Config.REDIS_DB, 
                 retry_on_timeout: bool = Config.REDIS_RETRY_ON_TIMEOUT, 
                 decode_responses: bool = Config.REDIS_DECODE_RESPONSE):
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            max_connections=max_connections,
            retry_on_timeout=retry_on_timeout,
            decode_responses=decode_responses
        )
    
    async def close(self):
        """Close all connections in the pool."""
        await self.pool.disconnect()