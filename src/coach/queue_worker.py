import os
import json
import pika
from pydantic import BaseModel, ValidationError
from services.wod_service import generate_daily_wod_for_user

# Define message schema
class WodMessage(BaseModel):
    email: str
    date: str

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        message = WodMessage(**data)

        print(f"✅ Received valid message: {message}")
        generate_daily_wod_for_user(message.email, message.date)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except (json.JSONDecodeError, ValidationError) as e:
        print(f"❌ Invalid message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    except Exception as e:
        print(f"❌ Error while processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
        os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=5672,
        credentials=credentials
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    queue_name = "createWodQueue"
    channel.queue_declare(queue=queue_name, durable=True)

    print("🎧 Waiting for messages. To exit press CTRL+C")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()

if __name__ == "__main__":
    main()
