import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    def __init__(self):
        self.uri = os.environ.get('MONGODB_URI', 'mongodb+srv://mongodb.g3jersh.mongodb.net/')
        
        self.cert_path = os.environ.get('MONGODB_CERT_PATH', '/app/certs/mongodb.pem') #'/home/taggioml/.ssh/X509-cert-3705830648530031648.pem')
        self.db_name = os.environ.get('MONGODB_DB_NAME', 'Subscription')
        self.collection_name = os.environ.get('MONGODB_COLLECTION', 'address')
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    @retry(
        stop=stop_after_attempt(3),
        # stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((ServerSelectionTimeoutError, AutoReconnect)),
        before_sleep=lambda retry_state: logger.warning(f"Retrying MongoDB connection: attempt {retry_state.attempt_number}")
    )

    def connect(self):
        """Establish MongoDB connection with TLS and X509 authentication"""
        try:
            self.client = MongoClient(
                self.uri,
                tls=True,
                # ssl=True,
                tlsCertificateKeyFile=self.cert_path,
                authSource='$external',
                authMechanism='MONGODB-X509',
                # appName='Cluster0',
                serverSelectionTimeoutMS=30000,
                retryWrites=True,
                w='majority',
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                tlsAllowInvalidCertificates=False 
                #socketKeepAlive=True, 
                #connect=False, 
                #maxPoolsize=1
            )
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            self.client.admin.command('ping')
            logger.info("MongoDB connection established")
        except ServerSelectionTimeoutError as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
    ##### -------- #####
    def get_collection(self):
        """Return the MongoDB collection"""
        return self.collection

    def __del__(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    ##### -------- #####
    def insert_address(self, address_data):
        try:
            result = self.collection.insert_one(address_data)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to insert address: {str(e)}")
            raise

    def get_all_addresses(self):
        try:
            return list(self.collection.find({'address': {'$ne': None}}))
        except Exception as e:
            logger.error(f"Failed to retrieve addresses: {str(e)}")
            raise