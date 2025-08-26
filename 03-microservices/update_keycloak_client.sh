# #!/bin/bash
set -euo pipefail

HOST_IP=$(hostname -I | cut -f1 -d' ')
REALM="subscription_realm"
CLIENT_ID="subscription_client"
IS_AUTH=false
IS_CLIENT=false

echo "Updating Keycloak client for IP: $HOST_IP"

# Function to validate token format
validate_token() {
    local token="$1"
    # Check if token is not empty and follows JWT pattern (three parts separated by dots)
    if [[ -z "$token" || "$token" == "null" ]]; then
        return 1
    fi
    
    # Basic JWT pattern validation (header.payload.signature)
    local parts
    IFS='.' read -ra parts <<< "$token"
    if [[ ${#parts[@]} -ne 3 ]]; then
        return 1
    fi
    
    # Check if parts are base64url encoded (should contain only alphanumeric, -, _)
    for part in "${parts[@]}"; do
        if ! [[ "$part" =~ ^[a-zA-Z0-9_-]+$ ]]; then
            return 1
        fi
    done
    
    return 0
}

# Get admin access token
ADMIN_TOKEN=$(curl -k -s -X POST \
  "https://$HOST_IP:8080/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" | jq -r '.access_token')

# Validate token format
if ! validate_token "$ADMIN_TOKEN"; then
    echo "❌ Failed to get valid admin token"
    echo "Token received: '$ADMIN_TOKEN'"
    exit 1
fi

echo "✅ Admin token format is valid"

# Get client UUID
CLIENT_UUID=$(curl -k -s -X GET \
    "https://$HOST_IP:8080/admin/realms/$REALM/clients?clientId=$CLIENT_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

if [ -z "$CLIENT_UUID" ] || [ "$CLIENT_UUID" = "null" ]; then
    echo "❌ Client '$CLIENT_ID' not found in realm '$REALM'"
    exit 1
else
    echo "✅ Client '$CLIENT_ID' found in realm '$REALM'"
fi

    # Get current client configuration
CURRENT_CONFIG=$(curl -k -s -X GET \
    "https://$HOST_IP:8080/admin/realms/$REALM/clients/$CLIENT_UUID" \
    -H "Authorization: Bearer $ADMIN_TOKEN")

# Update the configuration
UPDATED_CONFIG=$(echo "$CURRENT_CONFIG" | jq \
    --arg ip "$HOST_IP" \
    '.redirectUris = ["https://\($ip):8000/oidc/callback/*"] | 
    .webOrigins = ["https://\($ip):8000"]')

# Send the update using the correct endpoint
RESPONSE=$(curl -k -s -w "%{http_code}" -X PUT \
    "https://$HOST_IP:8080/admin/realms/$REALM/clients/$CLIENT_UUID" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$UPDATED_CONFIG")
HTTP_CODE=${RESPONSE: -3}

if [ "$HTTP_CODE" -eq 204 ]; then
    echo "✅ Client updated successfully"
    echo "Redirect URIs set to: https://$HOST_IP:8000/oidc/callback/*"
    echo "Web Origins set to: https://$HOST_IP:8000"
else
    echo "❌ Failed to update client. HTTP code: $HTTP_CODE"
    echo "Response: ${RESPONSE%???}"
    exit 1
fi



