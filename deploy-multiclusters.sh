#!/bin/bash
set -euo pipefail

TARGET=${1:-dev}
VAULT_CTX=kind-cluster-a
APP_CTX=kind-cluster-b

# Clean up previous job if exists
kubectl --context $VAULT_CTX delete job -n ms-demo-dev extract-vault-vars --ignore-not-found

# Phase 1: Prerequisites
echo "=== Phase 1: Deploying Prerequisites ==="
kluctl deploy -t dev --context $VAULT_CTX --arg deployment_phase=phase1
kluctl deploy -t dev --context $APP_CTX --arg deployment_phase=phase1

# # Phase 2: Variable Extraction
#echo "=== Phase 2: Extracting Variables ==="
#kluctl deploy -t dev --context $VAULT_CTX --arg deployment_phase=phase2

# Phase 2: Variable Extraction (now local)
echo "=== Phase 2: Extracting Variables Locally ==="
#./hooks/vault-vars-extractor/extract.sh $TARGET
bash .secrets/extract_vault_vars.sh 

# After ConfigMap creation, before phase3
# echo "=== Verifying ConfigMap Variables ==="
# kubectl --context $VAULT_CTX get configmap vault-crosscluster-vars -n ms-demo-dev \
#   -o jsonpath='{.data.vault-vars\.yaml}' | grep -q "vault_root_token" || {
#   echo "❌ Required variables missing in ConfigMap"
#   exit 1
# }

# # Phase 3: Main Deployment
echo "=== Phase 3: Main Deployment ==="
kluctl deploy -t $TARGET --context $VAULT_CTX --arg deployment_phase=phase3
kluctl deploy -t $TARGET --context $APP_CTX --arg deployment_phase=phase3


# #PHASE1: kluctl deploy -t vault-dev
# deployments:
#   - path: 01-namespaces     # Namespace creation
#   - barrier: true 
#   - path: 02-third-party/01-vault   #  Vault deployment (vault-dev only)
  
# #PHASE2: kluctl deploy -t app-dev
# deployments:
#   - path: 01-namespaces     # Namespace creation
#   - barrier: true 
#   - path: 02-third-party/02-vso/serviceaccount # VSO serviceaccount (app-dev only)

# #PHASE3:
# # ---- MANUAL STEP: Run .secrets/extract_vault_vars.sh here ----
# # (pause Kluctl, run the script, then resume Kluctl)

# #PHASE4: kluctl deploy -t app-dev
# deployments:
#   - path: 01-namespaces     # Namespace creation
#   - barrier: true 
#   - path: 02-third-party/02-vso/serviceaccount #  VSO serviceaccount (app-dev only)
#   - path: 02-third-party/02-vso/operator # PHASE 4-6:  VSO deployment (app-dev only)

# #PHASE5: kluctl deploy -t vault-dev
# deployments:
#   - path: 01-namespaces     # Namespace creation
#   - barrier: true 
#   - path: 02-third-party/01-vault   #  Vault deployment (vault-dev only)
#   - barrier: true 
#   - path: 03-vault-setup    #  Vault configuration job (vault-dev only)
  
#  #PHASE6: kluctl deploy -t app-dev
# deployments:
#   - path: 01-namespaces     # Namespace creation
#   - barrier: true 
#   - path: 02-third-party/02-vso/serviceaccount # VSO serviceaccount (app-dev only)
#   - path: 02-third-party/02-vso/operator # VSO deployment (app-dev only)
#   - path: 04-vaultsecret    # VaultSecret CRD (app-dev only)
