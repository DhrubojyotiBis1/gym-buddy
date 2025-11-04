class Config:
    MAX_GRPC_WORKER = 10
    GRPC_IP = "0.0.0.0"
    GRPC_PORT = "50051"
    JWT_ALGORITHM = "ES256"
    PUBLIC_KEY_PATH = "public_key.pem"
    USER_DB_USER = "postgres"
    USER_DB_PASSWORD = "postgres"
    USER_DB_NAME = "gym_buddy"
    USER_DB_HOST = "postgres"  
    USER_DB_PORT = "5432"
    