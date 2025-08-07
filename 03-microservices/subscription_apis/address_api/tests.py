# address_api/tests.py
from django.test import TestCase
from rest_framework.test import APITestCase
from .mongodb import get_collection, get_all_addresses_from_mongo

class AddressTests(APITestCase):
    def setUp(self):
        # Clear collection before test
        get_collection().delete_many({})

    def test_create_address(self):
        data = {
            "name": "A. Anderson",
            "address": "Down Under 1",
            "postalcode": "ZPT 1",
            "city": "Gotham",
            "country": "Northland",
            "email": "anderson@upside.com"
        }
        response = self.client.post('/api/v1/addresses/', data, format='json')
        self.assertEqual(response.status_code, 201)

        # Check MongoDB
        addresses = get_all_addresses_from_mongo()
        self.assertEqual(len(addresses), 1)
        self.assertEqual(addresses[0]['name'], 'A. Anderson')

    def test_postalcode_max_length(self):
        data = {
            "postalcode": "1234567890123456"  # 16 chars
        }
        response = self.client.post('/api/v1/addresses/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Ensure this field has no more than 15 characters', str(response.content))