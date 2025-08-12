import datetime
import json
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost')
)

channel = connection.channel()

# sets up an exchange called email
# subscribes the worker to the email exchange
# but since the exchange creates temporary queues as needed, 
# the worker must determine the temporary queue.
channel.exchange_declare(
    exchange='email',
    exchange_type='fanout'
    )

# collects the temporary task queue
result = channel.queue_declare(
    queue = '', 
    exclusive = True
    )

# determines the name of the temporary queue
queue_name = result.method.queue

# connects the worker to the temporary queue.
channel.queue_bind(
    exchange = 'email',
    queue = queue_name
)

# declares a callback function that executes whenever 
# the worker picks up a task. Within this function

def callback(ch, method, properties, body):
    # parses the task
    mail_message = json.loads(body)

    now = datetime.datetime.now()
    # simulates sending an email
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] email sent to {mail_message['name']}"
    )

# make the worker listen for new tasks in the mail_queue task
# taps the tasks from the temporary task queue and 
# executes the callback function for each task
channel.basic_consume(
    queue = queue_name,
    on_message_callback = callback,
    auto_ack = True
)

channel.start_consuming()