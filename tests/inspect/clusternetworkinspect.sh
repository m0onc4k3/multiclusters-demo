#!/bin/bash

# Check for argument
if [ -z "$1" ]; then
  echo "Usage: $0 <cluster-name>"
  echo "Example: $0 cluster-b"
  exit 1
fi

CLUSTER_NAME="$1"
CONTEXT="kind-$CLUSTER_NAME"

echo "=== Gathering data for cluster: $CLUSTER_NAME, context: $CONTEXT ==="
echo

# Verify kubectl context exists
if ! kubectl config get-contexts "$CONTEXT" -o name >/dev/null 2>&1; then
  echo "❌ Error: Kubernetes context '$CONTEXT' not found."
  echo "Available contexts:"
  kubectl config get-contexts -o name
  exit 1
fi

# Set kubectl to use this context
KUBECTL="kubectl --context $CONTEXT"

# Map: Docker container name → IP (only for this cluster)
declare -A NODE_IPS
while IFS='=' read -r name ip; do
  NODE_IPS["$name"]="${ip%/16}"  # Remove /16 if present
done < <(
  docker network inspect kind \
    | jq -r '.[0].Containers[] | select(.Name | startswith("'"$CLUSTER_NAME"'")) | "\(.Name)=\(.IPv4Address)"'
)

# Print header
printf "%-30s %-15s %-50s %-15s %-20s\n" "NODE (K8s)" "NODE_IP (Docker)" "POD_NAME" "POD_IP" "NAMESPACE"
printf "%-30s %-15s %-50s %-15s %-20s\n" "-----------------------------" "---------------" "----------------------------------------" "---------------" "--------------------"

# Get pods from the cluster
$KUBECTL get pods -A -o json \
  | jq -r '.items[] | "\(.spec.nodeName) \(.metadata.name) \(.status.podIP) \(.metadata.namespace)"' \
  | while read -r k8s_node pod_name pod_ip ns; do
      # Try both possible Docker container names
      docker_name="$CLUSTER_NAME-$k8s_node"
      node_ip="${NODE_IPS[$docker_name]}"

      # Fallback: maybe it's the control-plane directly named
      if [ -z "$node_ip" ] && [ "$k8s_node" = "control-plane" ]; then
        node_ip="${NODE_IPS["${CLUSTER_NAME}-control-plane"]}"
      fi

      # Fallback: direct match
      if [ -z "$node_ip" ]; then
        node_ip="${NODE_IPS[$k8s_node]}"
      fi

      printf "%-30s %-15s %-50s %-15s %-20s\n" "$k8s_node" "$node_ip" "$pod_name" "$pod_ip" "$ns"
    done