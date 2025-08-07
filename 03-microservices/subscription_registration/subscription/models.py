# subscription/models.py
from django.db import models
#from subscription.mongodb import get_collection  # ← New module (see below)
from datetime import datetime

class Address(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=120)
    postalcode = models.CharField(max_length=20)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=80)
    email = models.EmailField()

    # Disable Django ORM save
    # def save(self, *args, **kwargs):
    #     # Do NOT call super() — bypass ORM
    #     # Instead, use custom MongoDB save
    #     self.save_to_mongo()

    # def save_to_mongo(self):
    #     collection = get_collection()
    #     doc = {
    #         'name': self.name,
    #         'address': self.address,
    #         'postalcode': self.postalcode,
    #         'city': self.city,
    #         'country': self.country,
    #         'email': self.email,
    #         'created_at': datetime.utcnow()
    #     }
    #     collection.insert_one(doc)

    # class Meta:
    #     # Prevent Django from managing this model in DB
    #     managed = False
    #     # Optional: name collection explicitly
    #     db_table = 'address'  # MongoDB collection name