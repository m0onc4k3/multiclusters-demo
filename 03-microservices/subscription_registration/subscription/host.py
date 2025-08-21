# # non container setup
# import socket 

# def get_local_ip():
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.connect(("8.8.8.8", 80))
#             # print(s.getsockname()[0])
#             return s.getsockname()[0]
#     except Exception:
#         # print("127.0.0.1")
#         return "127.0.0.1"

# containerized setup
import os
import logging

logger = logging.getLogger(__name__)

def get_cookies_url():
    #host_ip = get_local_ip()
    host_ip = os.environ.get('SUBSCRIPTION_APIS_HOST', 'subscription-apis')
    logger.info(f"SUBSCRIPTION_APIS_HOST: {host_ip}")
    cookies_url = f'http://{host_ip}:7000/api/v1/token/'
    return cookies_url

def get_subscription_url():
    #host_ip = get_local_ip()
    host_ip = os.environ.get('SUBSCRIPTION_APIS_HOST', 'subscription-apis')
    subscription_url = f'http://{host_ip}:7000/api/v1/addresses/'
    return subscription_url