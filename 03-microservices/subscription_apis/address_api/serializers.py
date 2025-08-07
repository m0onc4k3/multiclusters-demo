from rest_framework import serializers
from datetime import datetime

class AddressSerializer(serializers.Serializer):
    _id = serializers.CharField(required=False)  # Optional for response
    name = serializers.CharField(max_length=120, allow_blank=False)
    address = serializers.CharField(max_length=120, allow_blank=False)
    postalcode = serializers.CharField(max_length=20, allow_blank=False)
    city = serializers.CharField(max_length=120, allow_blank=False)
    country = serializers.CharField(max_length=80, allow_blank=False)
    email = serializers.EmailField(allow_blank=False)
    created_at = serializers.DateTimeField(read_only=True, default=datetime.utcnow)

    def create(self, validated_data):
        validated_data['created_at'] = datetime.utcnow()
        return validated_data

    def update(self, instance, validated_data):
        instance.update(validated_data)
        instance['created_at'] = instance.get('created_at', datetime.utcnow())
        return instance
        
    def validate(self, data):
        """Ensure no fields are empty strings"""
        for field in ['name', 'address', 'postalcode', 'city', 'country', 'email']:
            if not data.get(field).strip():
                raise serializers.ValidationError({field: "This field cannot be empty."})
        return data