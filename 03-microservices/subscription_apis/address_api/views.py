from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddressSerializer
from .mongodb import MongoDBClient
from bson import ObjectId
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from datetime import datetime

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            refresh_token = response.data['refresh']
            response.set_cookie(
                key='access_token',
                value=access_token,
                max_age=60 * 60,  # 60 minutes
                httponly=True,
                # [ ]: Set to False for local testing without HTTPS
                secure=False,  
                # [ ]: Set to None in production
                samesite='Lax', 
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                max_age=24 * 60 * 60,  # 1 day
                httponly=True,
                secure=False,  # [ ]: Set to False for local testing
                samesite='Lax', # [ ]: Set to None in production
            )
            # Remove tokens from response body
            response.data = {'message': 'Login successful'}
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            response.set_cookie(
                key='access_token',
                value=access_token,
                max_age=60 * 60,
                httponly=True,
                secure=False,  # Set to False for local testing
                samesite='Lax', # []: Set to None in production
            )
            response.data = {'message': 'Token refreshed'}
        return response

class AddressListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = MongoDBClient()
        collection = client.get_collection()
        addresses = list(collection.find())
        for address in addresses:
            address['_id'] = str(address['_id'])
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            client = MongoDBClient()
            collection = client.get_collection()
            validated_data = serializer.validated_data
            validated_data['created_at'] = datetime.utcnow()  # Add created_at
            result = collection.insert_one(validated_data)
            inserted_id = str(result.inserted_id)
            validated_data['_id'] = inserted_id
            return Response(
                validated_data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, id):
        client = MongoDBClient()
        collection = client.get_collection()
        try:
            address = collection.find_one({'_id': ObjectId(id)})
            if not address:
                raise Http404
            address['_id'] = str(address['_id'])
            return address
        except ValueError:
            raise Http404

    def get(self, request, id):
        address = self.get_object(id)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, id):
        address = self.get_object(id)
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            client = MongoDBClient()
            collection = client.get_collection()
            validated_data = serializer.validated_data
            validated_data['created_at'] = address.get('created_at', datetime.utcnow())
            collection.replace_one({'_id': ObjectId(id)}, validated_data)
            return Response(validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id):
        address = self.get_object(id)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            client = MongoDBClient()
            collection = client.get_collection()
            validated_data = serializer.validated_data
            validated_data['created_at'] = address.get('created_at', datetime.utcnow())
            collection.update_one({'_id': ObjectId(id)}, {'$set': validated_data})
            updated_address = collection.find_one({'_id': ObjectId(id)})
            updated_address['_id'] = str(updated_address['_id'])
            return Response(AddressSerializer(updated_address).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            client = MongoDBClient()
            collection = client.get_collection()
            result = collection.delete_one({'_id': ObjectId(id)})
            if result.deleted_count == 0:
                raise Http404
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            raise Http404