import os
import pika
import json
from typing import Dict, Any

def validate_message_format(message: Dict[str, Any]) -> bool:
    return (
        isinstance(message, dict)
        and "email" in message
        and isinstance(message["email"], str)
        and "date" in message
        and isinstance(message["date"], str)
    )

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = "createWodQueue"
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ server"""
        credentials = pika.PlainCredentials(
            username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
            password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=5672,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        arguments = {
            "x-message-ttl": 60000,  # 1 minute
            "x-max-length": 100,
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": f"{self.queue_name}-dead"
        }

        self.channel.exchange_declare(exchange="dlx", exchange_type="direct")
        self.channel.queue_declare(queue=f"{self.queue_name}-dead", durable=True)
        self.channel.queue_bind(
            exchange="dlx",
            queue=f"{self.queue_name}-dead",
            routing_key=f"{self.queue_name}-dead"
        )

        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments=arguments
        )

    def publish_message(self, message: Dict[str, Any]) -> bool:
        """Publish a message to the queue"""
        try:
            if not validate_message_format(message):
                print("Invalid message format:", message)
                return False

            if not self.connection or self.connection.is_closed:
                self.connect()

            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            return True
        except Exception as e:
            print(f"Error publishing message to RabbitMQ: {str(e)}")
            return False

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

# Do not connect on import
rabbitmq_service = None

def get_rabbitmq_service():
    global rabbitmq_service
    if rabbitmq_service is None:
        rabbitmq_service = RabbitMQService()
    return rabbitmq_service
