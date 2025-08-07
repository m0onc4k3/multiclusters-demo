#!/bin/bash

# Configuration
LOGIN_URL="http://127.0.0.1:7000/api/v1/token/"
API_URL="http://127.0.0.1:7000/api/v1/addresses/"
USERNAME="taggioml03"
PASSWORD="password987"
FORM_DATA='{"name": "Jude Bellingham", "address": "Valdebebas", "postalcode": "777777", "city": "Madrid", "country": "Spain", "email": "jude@madrid.com"}'

# Step 1: Login and get access_token
RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" \
  -c cookies.txt)

# Step 2: Extract access_token from cookies.txt
ACCESS_TOKEN=$(grep "access_token" cookies.txt | awk '{print $7}')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to obtain access_token"
  exit 1
fi

echo "Access token: $ACCESS_TOKEN"

# Step 3: Send form data with access_token
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=$ACCESS_TOKEN" \
  -d "$FORM_DATA"