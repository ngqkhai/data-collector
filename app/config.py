import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Service configuration
SERVICE_NAME = "wikipedia-collector-service"
PORT = int(os.environ.get("PORT"))
DEBUG = os.environ.get("DEBUG").lower() == "true"
ENV = os.environ.get("ENV")

# Database configuration
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB = os.environ.get("MONGO_DB")
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION")

SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]

# Maximum content length for requests
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 1 * 1024 * 1024))  # 1MB