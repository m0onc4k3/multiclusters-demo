# import os
# import tempfile
# import logging
# from pathlib import Path

# logger = logging.getLogger(__name__)

# class MongoDBCertificateManager:
#     """Manages MongoDB X.509 certificate at runtime"""
    
#     def __init__(self):
#         self.vault_secrets_path = os.getenv('VAULT_SECRETS_PATH', '/vault/secrets')
#         self.cert_storage_path = Path('/app/certs')  # Memory-backed volume
#         self.mongodb_cert_file = None
        
#     def setup_certificate(self):
#         """Create MongoDB certificate file from Vault injected secret"""
#         try:
#             # Ensure cert directory exists with proper permissions
#             self.cert_storage_path.mkdir(exist_ok=True, mode=0o700)
            
#             # Read certificate content from Vault injected file
#             cert_file_path = Path(self.vault_secrets_path) / 'mongodb-cert'
            
#             if not cert_file_path.exists():
#                 raise FileNotFoundError(f"Vault injected certificate not found at {cert_file_path}")
            
#             # Read certificate content
#             cert_content = cert_file_path.read_text().strip()
            
#             if not cert_content:
#                 raise ValueError("Certificate content is empty")
            
#             # Create certificate file in memory-backed storage
#             self.mongodb_cert_file = self.cert_storage_path / 'mongodb-client.pem'
#             self.mongodb_cert_file.write_text(cert_content)
#             self.mongodb_cert_file.chmod(0o600)  # Secure permissions
            
#             logger.info(f"MongoDB certificate created at {self.mongodb_cert_file}")
#             return str(self.mongodb_cert_file)
            
#         except Exception as e:
#             logger.error(f"Failed to setup MongoDB certificate: {e}")
#             raise
    
#     def get_mongodb_connection_string(self):
#         """Build complete MongoDB connection string with certificate"""
#         try:
#             # Setup certificate first
#             cert_path = self.setup_certificate()
            
#             # Read base URI from Vault injected config
#             config_file_path = Path(self.vault_secrets_path) / 'mongodb-config'
            
#             if not config_file_path.exists():
#                 raise FileNotFoundError(f"MongoDB config not found at {config_file_path}")
            
#             base_uri = config_file_path.read_text().strip()
            
#             # Build complete connection string
#             connection_string = f"{base_uri}&tlsCertificateKeyFile={cert_path}"
            
#             logger.info("MongoDB connection string configured successfully")
#             return connection_string
            
#         except Exception as e:
#             logger.error(f"Failed to setup MongoDB connection: {e}")
#             raise
    
#     def cleanup_certificate(self):
#         """Clean up certificate file (called on app shutdown)"""
#         if self.mongodb_cert_file and self.mongodb_cert_file.exists():
#             try:
#                 self.mongodb_cert_file.unlink()
#                 logger.info("MongoDB certificate cleaned up")
#             except Exception as e:
#                 logger.warning(f"Failed to cleanup certificate: {e}")

# # Global instance
# mongodb_cert_manager = MongoDBCertificateManager()

# def get_mongodb_connection_string():
#     """Public function to get MongoDB connection string"""
#     return mongodb_cert_manager.get_mongodb_connection_string()

# # Django settings integration
# def load_vault_secrets():
#     """Load secrets from Vault injected files"""
#     secrets = {}
#     vault_secrets_path = Path(os.getenv('VAULT_SECRETS_PATH', '/vault/secrets'))
    
#     # Load Django secrets
#     django_secrets_file = vault_secrets_path / 'django-secrets'
#     if django_secrets_file.exists():
#         for line in django_secrets_file.read_text().strip().split('\n'):
#             if '=' in line:
#                 key, value = line.split('=', 1)
#                 secrets[key] = value
    
#     return secrets