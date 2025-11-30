class Config:
    # -------- Logger Settings --------
    LOG_FORMATER = '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'

    # -------- Redis Settings --------
    REDIS_HOSTNAME = 'redis'
    REDIS_PORT = '6379'
    REDIS_MAX_CONNECTION = 20
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_DECODE_RESPONSE = True
    REDIS_DB = 0
    REDIS_SET_KEY = 'SET'
    REDIS_BIDS_KEY = 'BIDS'
    REDIS_STREAM_KEY = 'STREAM'
    REDIS_BIDS_RETRY_COUNT = 3

    # -------- JWT & Security --------
    JWT_ALGORITHM = "ES256"
    PUBLIC_KEY_PATH = "public_key.pem"

    # -------- Service/Cache Identifiers --------
    SERVICE_HOST = 'direct_chat'
    SERVICE_PORT = '50052'
    USERS_CONVERSATION_ID_PREFIX = "participants:conversation_id:"
    CONVERSATION_ID_USER_PREFIX = "conversation_id:participants:"
    CONNECTED_USER_PREFIX = "user:service:"

    # -------- Kafka Settings --------
    TOPIC_MESSAGES = 'messages'
    TOPIC_STORAGE = 'storage'
    KAFKA_BOOTSTRAP_SERVERS = "kafka:9094"
    KAFKA_CLIENT_ID = "direct-chat-service"
    KAFKA_TRANSACTION_ID = "test-transaction"

    # -------- Database Settings --------
    DB_HOST = "postgres"  
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    DB_NAME = "gym_buddy"

    # -------- gRPC Settings --------
    GRPC_IP = "0.0.0.0"
    GRPC_PORT = "50052"
