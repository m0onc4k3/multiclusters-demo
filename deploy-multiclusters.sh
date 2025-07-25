#!/bin/bash
set -euo pipefail

TARGET=${1:-dev}
VAULT_CTX=kind-cluster-a
APP_CTX=kind-cluster-b

# Clean up previous job if exists
kubectl --context $VAULT_CTX delete job -n ms-demo-$TARGET extract-vault-vars --ignore-not-found

# Phase 1: Deploy Vault and VSO serviceaccount
echo "=== Phase 1: Deploying Vault and VSO serviceaccount ==="
kluctl deploy -t $TARGET --context $VAULT_CTX --arg deployment_phase=phase1
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase1

# Phase 2: Variable Extraction (local)
echo "=== Phase 2: Extracting Variables Locally ==="
bash .secrets/extract_vault_vars.sh 

# Phase 3: vault setup and VSO operator deployment
echo "=== Phase 3: Vault setup and VSO operator deployment ==="
kluctl deploy -t $TARGET --context $VAULT_CTX --arg deployment_phase=phase3
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase3

# Phase 4: Create ricoberber vaultsecret
echo "=== Phase 4: Create and retrieve ricoberger Vaultsecret ==="
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase4

# Phase 5: Create ricoberber vaultsecret
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase5
kluctl prune -t $TARGET --context $APP_CTX --arg deployment_phase=phase5