import json
import pika
import uuid

class Mailer(object):
    # initialize the connection to RabbitMQ
    def __init__(self):
        # Standard practice
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost')
            )
        
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(
            queue='',
            exclusive=True
        )
        
        # request-response specific
        # set up a callback queue for responses
        # the on_response method should be executed 
        # when a message (response) arrives in the callback queue
        self.callback_queue = result.method.queue
        self.channel.basic_consume(
            queue = self.callback_queue,
            on_message_callback = self.on_response,
            auto_ack=True
        )
        # corr_id holds the correlation ID that 
        # uniquely connects a task and its corresponding response
        self.response = None
        self.corr_id = None
    
    # set the response when it's received from the worker
    # set the correlation ID of the task and the response match
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    # the entry point for offloading a task to a microservice worker
    def call(self, mail_task):
        self.response = None
        # creates an universal unique identifier for correlation ID
        self.corr_id = str(uuid.uuid4())
        # set the task queue with pika properties
        self.channel.basic_publish(
            exchange='',
            routing_key='mail_queue',
            properties=pika.BasicProperties(
                # assign the callback queue where the worker should drop the response
                reply_to=self.callback_queue,
                # exchange the generated UUID to the worker
                correlation_id=self.corr_id,
            ),
            body=json.dumps(mail_task)    
        )
        self.connection.process_data_events(
            # endless
            time_limit=None
        )
        # return the actual response from the worker
        return self.response

# setting the task
mail_task = {
    'name': f'M. McDoe',
    'email': f'mcdoe@yyz.com',
    'subject': 'Our Django offer',
    'body': 'Dear...'
}

mailer = Mailer()
response = mailer.call(mail_task)
# decode the byte string response and print it out
print(response.decode('utf-8'))