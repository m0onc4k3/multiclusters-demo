#!/bin/bash
# PHASE 2: Extracts cross-cluster values for Vault Kubernetes auth

set -euo pipefail
#Change kind context
kubectl config use-context kind-cluster-a

echo "Extracting vault root token..."
#VAULT_ROOT_TOKEN="root"
VAULT_ROOT_TOKEN=$(kubectl logs vault-0 -n ms-demo-dev | grep "Root Token:" | awk '{print $NF}')

VARS_FILE="$(dirname "$0")/.vault-crosscluster-vars.yaml"

echo "Extracting cluster-a IP..."
CLUSTER_A_IP=$(docker inspect cluster-a-control-plane --format '{{ .NetworkSettings.Networks.kind.IPAddress }}' | tr -d '\n')

echo "Extracting cluster-b IP..."
CLUSTER_B_IP=$(docker inspect cluster-b-control-plane --format '{{ .NetworkSettings.Networks.kind.IPAddress }}' | tr -d '\n')
CLUSTER_B_API="https://${CLUSTER_B_IP}:6443"

echo "Extracting cluster-b CA cert..."
CLUSTER_B_CA_CERT=$(kubectl --context kind-cluster-b config view --raw -o jsonpath='{.clusters[?(@.name=="kind-cluster-b")].cluster.certificate-authority-data}' | base64 --decode)
CLUSTER_B_CA_CERT_B64=$(echo "$CLUSTER_B_CA_CERT" | base64 | tr -d '\n')

echo "Waiting for ServiceAccount 'vault-auth' in ms-demo-dev..."
kubectl --context kind-cluster-b -n ms-demo-dev wait --for=condition=Ready serviceaccount/vault-auth --timeout=60s || true

echo "Creating reviewer JWT..."
TOKEN_REVIEWER_JWT=$(kubectl --context kind-cluster-b -n ms-demo-dev create token vault-auth --duration=8760h)

cat > "$VARS_FILE" <<EOF
vault_root_token: "$VAULT_ROOT_TOKEN"
vault_cluster_a_ip: "$CLUSTER_A_IP"
cluster_b_api: "$CLUSTER_B_API"
cluster_b_ca_cert: |-
$(echo "$CLUSTER_B_CA_CERT" | sed 's/^/  /')
cluster_b_ca_cert_b64: "$CLUSTER_B_CA_CERT_B64"
token_reviewer_jwt: "$TOKEN_REVIEWER_JWT"
EOF

chmod 600 "$VARS_FILE"
echo "Wrote $VARS_FILE"