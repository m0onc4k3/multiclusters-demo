# address_api/models.py
from django.db import models

class Address(models.Model):
    name = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=120, blank=True)
    postalcode = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=80, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        # Import inside method to avoid circular import
        from .mongodb import save_address_to_mongo
        save_address_to_mongo(self)
        # Optionally call super() only if you want SQLite fallback
        # super().save(*args, **kwargs)

    class Meta:
        managed = False
        

    # def delete(self, *args, **kwargs):
    #     # Optional: implement delete in MongoDB
    #     from .mongodb import delete_address_from_mongo
    #     delete_address_from_mongo(self.id)
    #     super().delete(*args, **kwargs)

    # class Meta:
    #     managed = False  # Don't create migrations