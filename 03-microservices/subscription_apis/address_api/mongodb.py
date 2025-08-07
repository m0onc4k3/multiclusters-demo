import os
from pymongo import MongoClient

class MongoDBClient:
    def __init__(self):
        self.uri = os.environ.get('MONGODB_URI', 'mongodb+srv://ac-87iyiqj-shard-00-01.g3jersh.mongodb.net/')
        self.cert_path = os.environ.get('MONGODB_CERT_PATH', '/home/taggioml/.ssh/X509-cert-3705830648530031648.pem')
        self.db_name = os.environ.get('MONGODB_DB_NAME', 'Subscription')
        self.collection_name = os.environ.get('MONGODB_COLLECTION', 'address')
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        """Establish MongoDB connection with TLS and X509 authentication"""
        self.client = MongoClient(
            self.uri,
            tls=True,
            tlsCertificateKeyFile=self.cert_path,
            authSource='$external',
            authMechanism='MONGODB-X509',
            appName='Cluster0',
            serverSelectionTimeoutMS=30000,
            retryWrites=True,
            w='majority',
            connectTimeoutMS=30000,
            socketTimeoutMS=30000, 
            #socketKeepAlive=True, 
            #connect=False, 
            #maxPoolsize=1
        )
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def get_collection(self):
        """Return the MongoDB collection"""
        return self.collection

    def __del__(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()