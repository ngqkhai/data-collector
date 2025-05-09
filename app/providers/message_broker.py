import os
import logging
import aio_pika
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RabbitMQ Configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
DATA_COLLECTED_EXCHANGE = os.getenv("DATA_COLLECTED_EXCHANGE", "data_collected")
DATA_COLLECTED_ROUTING_KEY = os.getenv("DATA_COLLECTED_ROUTING_KEY", "data.collected")

logger = logging.getLogger(__name__)

class DataCollectorMessageBroker:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        logger.info("Initializing DataCollectorMessageBroker")

    async def connect(self):
        """Connect to RabbitMQ and setup exchanges"""
        try:
            # Create connection
            logger.info(f"Connecting to RabbitMQ at {RABBITMQ_URL}")
            self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
            logger.info("Successfully connected to RabbitMQ")

            # Create channel
            self.channel = await self.connection.channel()
            logger.info("Successfully created RabbitMQ channel")

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                DATA_COLLECTED_EXCHANGE,
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )
            logger.info(f"Successfully declared exchange: {DATA_COLLECTED_EXCHANGE}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def close(self):
        """Close RabbitMQ connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Successfully closed RabbitMQ connection")

    async def publish_data_collected(self, data: Dict[str, Any]):
        """Publish a message when new data is collected"""
        try:
            if not self.channel or not self.exchange:
                logger.error("Message broker not connected. Please call connect() first.")
                raise RuntimeError("Message broker not connected")

            # Convert data to JSON string
            json_data = json.dumps(data)
            # Log key fields to help with debugging
            logger.info(f"Publishing message with collection_id: {data.get('collection_id')}, source_type: {data.get('source_type')}")
            logger.info(f"Message routing key: {DATA_COLLECTED_ROUTING_KEY}")
            
            # Create message
            message = aio_pika.Message(
                body=json_data.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                # Add content_type header to help consumers
                content_type='application/json'
            )

            # Publish message
            logger.info(f"Publishing message to exchange {DATA_COLLECTED_EXCHANGE} with routing key {DATA_COLLECTED_ROUTING_KEY}")
            await self.exchange.publish(
                message,
                routing_key=DATA_COLLECTED_ROUTING_KEY
            )
            logger.info(f"Successfully published message with routing key: {DATA_COLLECTED_ROUTING_KEY}")

        except Exception as e:
            logger.error(f"Failed to publish data collected message: {str(e)}")
            raise 