from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_TITLE: str = "Data Collector API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for collecting data from various sources"
    API_PREFIX: str = "/api"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False
    ENV: str = "development"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # RabbitMQ Settings
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_EXCHANGE: str = "data_collected"
    RABBITMQ_QUEUE: str = "data_collected"
    RABBITMQ_ROUTING_KEY: str = "data.collected"
    
    # MongoDB Settings
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "data_collector")
    MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "collections")
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    MAX_CONTENT_LENGTH: int = 1 * 1024 * 1024  # 1MB
    ALLOWED_EXTENSIONS: set = {'.pdf', '.doc', '.docx'}
    SUPPORTED_FILE_TYPES: list = ["pdf", "docx", "txt"]
    
    # Service Settings
    SERVICE_NAME: str = "wikipedia-collector-service"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Create settings instance
settings = get_settings()
