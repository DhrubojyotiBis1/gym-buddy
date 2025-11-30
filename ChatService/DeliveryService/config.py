class Config:
    # -------- Logger Settings --------
    LOG_FORMATTER = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'

    # -------- Service Prefixes --------
    USERS_SERVICE_PREFIX = "user:service:"
    CONVERSATION_ID_USERS_PREFIX = "conversation_id:participants:"

    # -------- Kafka Settings --------
    KAFKA_CONSUMER_TOPIC = 'messages'
    KAFKA_CONSUMER_GROUP_ID = 'delivery-service'
    KAFKA_BOOTSTRAP_SERVERS = "kafka:9094"
    KAFKA_CLIENT_ID = ''
    KAFKA_TRANSACTIONAL_ID = ''

    # -------- Redis Settings --------
    REDIS_HOSTNAME = 'redis'
    REDIS_PORT = 6379
    REDIS_MAX_CONNECTION = 20
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_DECODE_RESPONSE = True
    REDIS_DB = 0
    REDIS_SET_KEY = 'SET'
    REDIS_BIDS_KEY = 'BIDS'
    REDIS_STREAM_KEY = 'STREAM'
    REDIS_BIDS_RETRY_COUNT = 3