#!/bin/bash
set -euo pipefail

echo "=============================================="
echo "🚀 LLM Platform Bootstrap"
echo "=============================================="

echo ""
echo "🔎 Current kubectl context:"
kubectl config current-context
echo ""

# --- Namespaces ---
echo "🗂 Ensuring namespaces exist..."
kubectl get ns llm >/dev/null 2>&1 || kubectl create namespace llm
kubectl get ns monitoring >/dev/null 2>&1 || kubectl create namespace monitoring
echo "✅ Namespaces ready"
echo ""

# --- Deploy Prometheus Stack FIRST ---
echo "📦 Deploying Prometheus Stack..."
helm upgrade --install prometheus ./platform/monitoring/prometheus-stack \
  -n monitoring \
  --wait \
  --timeout 5m

echo "⏳ Waiting for ServiceMonitor CRD to be available..."

until kubectl get crd servicemonitors.monitoring.coreos.com >/dev/null 2>&1; do
  echo "   ...still waiting for ServiceMonitor CRD"
  sleep 3
done

echo "✅ ServiceMonitor CRD is available"
echo ""

# --- Deploy LLM Runtime ---
echo "📦 Deploying LLM Runtime..."
helm upgrade --install llm-runtime ./charts/llm-runtime \
  -n llm \
  --wait \
  --timeout 5m

echo "✅ LLM Runtime deployed"
echo ""

# --- Deploy LLM API ---
echo "📦 Deploying LLM API..."
helm upgrade --install llm-api ./charts/llm-api \
  -n llm \
  --wait \
  --timeout 5m

echo "✅ LLM API deployed"
echo ""

# --- Apply ServiceMonitor (if external file) ---
if [ -f platform/monitoring/servicemonitor.yaml ]; then
  echo "📊 Applying ServiceMonitor manifest..."
  kubectl apply -f platform/monitoring/servicemonitor.yaml
  echo "✅ ServiceMonitor applied"
  echo ""
fi

echo "📊 Applying Grafana Dashboard..."
kubectl apply -f platform/monitoring/dashboards/llm-dashboard.yaml

# --- Final Status ---
echo "=============================================="
echo "🎉 Bootstrap Complete!"
echo "=============================================="
echo ""
echo "📌 Pods status:"
kubectl get pods -n llm
echo ""
kubectl get pods -n monitoring
echo ""