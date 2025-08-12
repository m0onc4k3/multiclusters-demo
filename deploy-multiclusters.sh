#!/bin/bash
set -euo pipefail

TARGET=${1:-dev}
VAULT_CTX=kind-cluster-a
APP_CTX=kind-cluster-b

echo; echo "=== Clean up previous job if exists ==="

kubectl --context $VAULT_CTX delete job -n ms-demo-$TARGET extract-vault-vars --ignore-not-found

# Phase 1: Deploy Vault server
echo; echo "=== Phase 1: Deploying Vault server ==="
kluctl deploy -t $TARGET --context $VAULT_CTX --arg deployment_phase=phase1 

# Wait for Vault StatefulSet to be ready
echo "=== Waiting for Vault to be ready in $VAULT_CTX ==="
kubectl --context $VAULT_CTX wait --for=condition=Ready pod -l app.kubernetes.io/instance=vault -n ms-demo-$TARGET --timeout=120s

# Phase 1: Deploy VSO serviceaccount
echo; echo "=== Phase 1: Deploying VSO serviceaccount ==="
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase1

# Phase 2-1: Variable Extraction (local)
echo; echo "=== Phase 2: Extracting Variables Locally ==="
bash .secrets/extract_vault_vars.sh 


# Phase 3: vault setup and VSO operator deployment
echo; echo "=== Phase 3: Vault setup and VSO operator deployment ==="
kluctl deploy -t $TARGET --context $VAULT_CTX --arg deployment_phase=phase3
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase3

# Phase 2-2: Some secrets (local)
echo; echo "=== Phase 2-2: Some secrets ==="
bash .secrets/credentials.sh

# Phase 4: Create ricoberber vaultsecret
echo; echo "=== Phase 4: Create and retrieve ricoberger Vaultsecret ==="
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase4

# Phase 5: Create rabbitmq operator and server
echo; echo "=== Phase 5: Create rabbitmq operator and server ==="
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase5
kluctl prune -t $TARGET --context $APP_CTX --arg deployment_phase=phase5

# # Phase 6: Create redis operator
# echo; echo "=== Phase 6: Create redis operator ==="
# kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase6
# # Phase 7: Create redis cluster
# echo; echo "=== Phase 7: Create redis cluster ==="
# kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase7

# Phase 6: Create redis 
# echo; echo "=== Phase 6: Create redis ==="
# kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase6

# echo; echo "=== Phase 6: Deploy django app ==="
# kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase7
