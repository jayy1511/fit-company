import pika
import json
import logging
from pymongo import MongoClient
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stats.queue_consumer")

# Connect to MongoDB
mongo = MongoClient("mongodb://stats_mongo:27017/")
db = mongo["stats_db"]
workout_stats = db["workout_stats"]

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        user_email = data["user_email"]
        generated_at = data["generated_at"]
        exercises = data["exercises"]

        # Save to MongoDB
        workout_stats.insert_one({
            "user_email": user_email,
            "generated_at": generated_at,
            "exercises": exercises
        })
        logger.info(f"✅ Stored workout for user {user_email} in MongoDB.")
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")

def start_stats_consumer():
    logger.info("🔁 Connecting to RabbitMQ...")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            credentials=pika.PlainCredentials(
                username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
                password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
            )
        )
    )
    channel = connection.channel()

    # Declare fanout exchange
    channel.exchange_declare(exchange='workout.performed', exchange_type='fanout')

    # Declare exclusive queue
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind to exchange
    channel.queue_bind(exchange='workout.performed', queue=queue_name)

    logger.info("📥 Waiting for messages on 'workout.performed' exchange. To exit press CTRL+C")
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()
