# # subscription/mongodb.py
# import os
# from pathlib import Path
# from pymongo import MongoClient
# from pymongo.database import Database

# # Environment variables
# MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb+srv://mongodb.g3jersh.mongodb.net/')
# MONGODB_CERT_PATH = os.environ.get('MONGODB_CERT_PATH', '/home/taggioml/.ssh/X509-cert-3705830648530031648.pem')
# MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'Subscription')
# MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION', 'address')

# # Validate cert file exists
# _cert_path = Path(MONGODB_CERT_PATH)
# if not _cert_path.exists():
#     raise FileNotFoundError(f"MongoDB X.509 certificate not found: {MONGODB_CERT_PATH}")

# _client = None
# _db = None

# def get_collection():
#     global _client, _db
#     if _db is None:
#         _client = MongoClient(
#             MONGODB_URI,
#             tls=True,
#             tlsCertificateKeyFile=str(_cert_path),
#             authSource='$external',
#             authMechanism='MONGODB-X509'
#         )
#         _db = _client[MONGODB_DB_NAME]
#     return _db[MONGODB_COLLECTION]