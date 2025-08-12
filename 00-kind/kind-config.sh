#!/bin/bash
set -e

kind create cluster --name cluster-a --config 00-kind/kind-config-a.yaml
kind create cluster --name cluster-b --config 00-kind/kind-config-b.yaml

# Deploy metrics server
kubectl --context kind-cluster-b  apply -f 00-kind/01-metrics-server/patch-metrics-server.yaml