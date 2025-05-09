import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any
from microservices.message_broker.client import MessageBroker
from microservices.message_broker.config import (
    DATA_COLLECTED_EXCHANGE,
    DATA_COLLECTED_ROUTING_KEY
)

# Add the message broker package to the Python path
message_broker_path = str(Path(__file__).parent.parent.parent / "microservices" / "message-broker")
sys.path.append(message_broker_path)

logger = logging.getLogger(__name__)

class DataCollectorMessageBroker:
    def __init__(self):
        self.broker = MessageBroker()

    async def connect(self):
        """Connect to RabbitMQ and setup exchanges/queues"""
        await self.broker.connect()
        await self.broker.setup_exchanges()
        await self.broker.setup_queues()

    async def close(self):
        """Close RabbitMQ connection"""
        await self.broker.close()

    async def publish_data_collected(self, data: Dict[str, Any]):
        """Publish a message when new data is collected"""
        try:
            await self.broker.publish_message(
                exchange=DATA_COLLECTED_EXCHANGE,
                routing_key=DATA_COLLECTED_ROUTING_KEY,
                message=data
            )
            logger.info(f"Published data collected message: {data}")
        except Exception as e:
            logger.error(f"Failed to publish data collected message: {str(e)}")
            raise

    async def start_consuming_script_generated(self, callback):
        """Start consuming script generated messages"""
        try:
            await self.broker.consume_script_generated(callback)
            logger.info("Started consuming script generated messages")
        except Exception as e:
            logger.error(f"Failed to start consuming script generated messages: {str(e)}")
            raise 