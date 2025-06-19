import pika
import json
import os

def publish_workout_created(workout_data):
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit")
    RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "docker")

    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue="workoutCreatedQueue", durable=True)

    # Publish message
    message = json.dumps(workout_data)
    channel.basic_publish(
        exchange="",
        routing_key="workoutCreatedQueue",
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    # Close after publishing to prevent stale connections
    connection.close()
