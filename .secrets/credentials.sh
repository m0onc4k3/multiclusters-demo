#!/bin/bash
set -euo pipefail

TARGET=${1:-dev}
VAULT_CTX=kind-cluster-a
gchr_crd_file=".secrets/credentials/ghcr.json"
vault_pod_name=vault-0
ghcr_secret_path=secret/ghcr/credentials

# Test if context exists
echo -e "\n===== Cluster context validation ====="
kubectl config get-contexts | grep $VAULT_CTX || {
    echo "❌ Error: $VAULT_CTX context not found"
    echo "Available contexts:"
    kubectl config get-contexts
    exit 1
}
echo "✅ $VAULT_CTX context found"

# Test if file exists
echo -e "\n===== Looking for ghcr credentials file ====="
[[ -f $gchr_crd_file ]] || { 
    echo "❌ Credentials file not found"
    exit 1
}
echo "✅ Credentiasl file found"

# Extract and validate
USERNAME=$(jq -r '.auths["ghcr.io"].username // empty' .secrets/credentials/ghcr.json)
PASSWORD=$(jq -r '.auths["ghcr.io"].password // empty' .secrets/credentials/ghcr.json)

echo -e "\n===== Checking non empty strings ====="
[[ -n "$USERNAME" && -n "$PASSWORD" ]] || { 
    echo "❌ empty strings present"
    exit 1
}
echo "✅ Non empty strings credentiasls"

echo -e "\n===== Creating vault secret ====="
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec $vault_pod_name -- vault kv put $ghcr_secret_path \
  username="$USERNAME" \
  password="$PASSWORD" >/dev/null 2>&1 && {
    echo "✅ Creation secret success"
} || {
    echo "❌ Failed to create secret"
    exit 1
}

##### ghcr policy:
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- /bin/sh -c \
  'echo -e "path \"secret/data/ghcr/credentials\" {\n    capabilities = [\"read\",\"list\"]\n}" > /tmp/ghcr-policy.hcl'

kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- sh -c "vault policy write ghcr-policy /tmp/ghcr-policy.hcl"

##### Store certificate content (base64 encoded for safety)
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- \
  sh -c  "vault kv put secret/mongodb/certificates client_cert='$(base64 -w 0 < $HOME/.ssh/X509-cert-3705830648530031648.pem)'" 

###### Store connection string template without file path
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- \
  sh -c "vault kv put secret/mongodb/connection \
  base_uri='mongodb+srv://mongodb.g3jersh.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&tls=true'"

##### mongodb certificates policy
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- /bin/sh -c \
  'echo -e "path \"secret/data/mongodb/certificates\" {\n    capabilities = [\"read\"]\n}" > /tmp/mongodb-cert-policy.hcl'

kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- sh -c "vault policy write mongodb-cert-policy /tmp/mongodb-cert-policy.hcl"

##### mongodb connection string policy
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- /bin/sh -c \
  'echo -e "path \"secret/data/mongodb/connection\" {\n    capabilities = [\"read\"]\n}" > /tmp/mongodb-cstr-policy.hcl'

kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- sh -c "vault policy write mongodb-cstr-policy /tmp/mongodb-cstr-policy.hcl"

# Bind the mongodb policies to a Kubernetes ServiceAccount:
kubectl --context $VAULT_CTX -n ms-demo-$TARGET exec vault-0 -- sh -c "vault write auth/kubernetes/role/mongodb-conn \
  bound_service_account_names='django-subscription' \
  bound_service_account_namespaces='ms-demo-dev' \
  policies='mongodb-cert-policy,mongodb-cstr-policy' \
  ttl=24h"