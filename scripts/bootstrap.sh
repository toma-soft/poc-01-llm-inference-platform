#!/bin/bash
set -e

echo "🚀 Starting bootstrap..."

echo "🔧 Creating namespaces..."
kubectl create namespace llm
kubectl create namespace monitoring

echo "📦 Deploying LLM runtime..."
helm upgrade --install llm-runtime ./charts/llm-runtime -n llm

echo "📦 Deploying LLM API..."
helm upgrade --install llm-api ./charts/llm-api -n llm

echo "📦 Deploying Prometheus stack..."
helm upgrade --install prometheus ./platform/monitoring/prometheus-stack -n monitoring

echo "📊 Applying ServiceMonitor..."
kubectl apply -f platform/monitoring/servicemonitor.yaml

echo "⏳ Waiting for pods..."
kubectl wait --for=condition=available deployment/llm-runtime -n llm --timeout=180s || true
kubectl wait --for=condition=available deployment/llm-api -n llm --timeout=180s || true

echo "✅ Bootstrap complete!"