import os
from django.urls import reverse
from dotenv import load_dotenv
from .mongodb import MongoDBConnection
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
import logging
from bson import ObjectId
from pprint import pprint 

logger = logging.getLogger(__name__)
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../', '.env'))

class AddressTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_username = os.getenv('TEST_USERNAME')
        cls.test_password = os.getenv('TEST_PASSWORD')
        # Create test user
        cls.user = User.objects.create_user(
            username=cls.test_username,
            password=cls.test_password
        )

        cls.host = 'http://127.0.0.1:7000'
        cls.login_url = cls.host + reverse('token_obtain_pair')
        cls.url = cls.host + reverse('address-list-create')
        cls.address_detail_url = lambda pk: f'{cls.host}/api/addresses/{pk}/'

    def setUp(self):
        # Get auth token
        auth_response = self.client.post(
            self.login_url,
            data = {'username': self.test_username, 
                    'password': self.test_password},
            format='json'
        )

        self.access_token = auth_response.cookies.get('access_token').value    

    def test_create_address(self):
        data = {
            "name": "A. Anderson",
            "address": "Down Under 1",
            "postalcode": "ZPT 1",
            "city": "Gotham",
            "country": "Northland",
            "email": "anderson@upside.com"
        }

        # 1. Connect to production collection
        prod_client = MongoDBConnection()
        
        # 2. Make API request
        response = self.client.post(
            self.url,
            data,
            format='json',
            HTTP_COOKIE=f'access_token={self.access_token}'
        )
        
        # 3. Verify response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        created_id = response_data['_id']
        
        # 4. Retrieve and display the full document from MongoDB
        document = prod_client.collection.find_one({"_id": ObjectId(created_id)})
        print("\n=== MongoDB Document Before Deletion ===")
        pprint(document)  # Pretty-print the full document
        print("===\n")
        
        # 5. Verify document content
        self.assertIsNotNone(document, "Document should exist in MongoDB")
        self.assertEqual(document['name'], data['name'])
        
        # 6. Cleanup
        delete_result = prod_client.collection.delete_one({"_id": ObjectId(created_id)})
        print(f"Deleted {delete_result.deleted_count} document(s)")
        prod_client.client.close()


    def test_create_address_postalcode_too_long(self):
        data = {"name": "C. Chai",
                "address": "Down Under 1",
                "postalcode": "ABCDEFGHIJ1234567890A",
                "city": "Gotham",
                "country": "Northland",
                "email": "chai@upside.com"
                }
        response = self.client.post(
            self.url, 
            data, 
            format='json',
            HTTP_COOKIE=f'access_token={self.access_token}'
            )
        response.render()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, b'{"postalcode":["Ensure this field has no more than 15 characters."]}')
