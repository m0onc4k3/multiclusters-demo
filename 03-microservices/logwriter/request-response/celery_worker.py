import datetime
from celery import Celery
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

#set rabbitmq as the message broker through the broker parameter and
# connects the worker with the log task queue
app = Celery(
    'log',
    broker='pyamqp://guest@localhost//'
    )

# decorates the write logitem function 
# which assigns the function as an asynchronous Celery driven task
@app.task()
def write_logitem(application, logmessage):
    now = datetime.datetime.now()
    #open the connection to mongoDB collection
    uri = os.environ.get('MONGODB_URI', 'mongodb+srv://ac-87iyiqj-shard-00-01.g3jersh.mongodb.net/')
    cert_path = os.environ.get('MONGODB_CERT_PATH', '/home/taggioml/.ssh/X509-cert-3705830648530031648.pem')
    db_name = os.environ.get('MONGODB_DB_NAME', 'Subscription')
    collection_name = os.environ.get('MONGODB_COLLECTION', 'subscription_logitem')
    client = MongoClient(
            uri,
            tls=True,
            tlsCertificateKeyFile=cert_path,
            authSource='$external',
            authMechanism='MONGODB-X509',
            appName='Cluster0',
            serverSelectionTimeoutMS=30000,
            retryWrites=True,
            w='majority',
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            server_api=ServerApi('1')
        )
    subscription_db = client[db_name]
    logitem_col = subscription_db[collection_name]
    # writes a log item to the collection
    logitem_col.insert_one(
        {
            'time': now.strftime(
                '%Y-%m-%d %H:%M:%s'
                ),
            'app': application,
            'logmessage': logmessage
        }
    )
    # print message to the terminal
    # print(f"""[{now.strftime('%Y-%m-%d %H:%M:%s')}] - new logmessage entered"""
    # )
    return 'Log message entered'