import json
import pika
import random

# connect the worker to RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost'
    )
)

channel = connection.channel()

channel.queue_declare(
    queue='mail_queue',
    durable=True
    )

# on request function
def on_request(ch, method, props, body):
    mail_message = json.loads(body)
    # emulates sending an email
    print(f"Email sent t {mail_message['name']}")
    # randomly set the response
    response = "OK" if random.choice([True, False]) == True else "NOK"
    # connect the worker to the callback queue where 
    # it must drop the response and correlation id that matches the response
    # and the originating task
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id
        ),
        body=response
    )
    # set the acknowlegment for the received task messages
    ch.basic_ack(delivery_tag=method.delivery_tag)

# set the quality of service for the comms between producer and worker
channel.basic_qos(prefetch_count=1)
# connect worker to the 'mail queue' task queue and
# sets the on_request function as the callback function to execute when tasks arrive
channel.basic_consume(
    queue='mail_queue',
    on_message_callback=on_request
)
channel.start_consuming()